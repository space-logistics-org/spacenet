"""
Object schemas for propellant logistics analysis: the contents of vehicle
tanks over time, propellant budgets, and the sizing of tanker campaigns to
aggregate propellant in a depot.
"""

import math
import re
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..records import PropellantFlow, PropellantFlowKind
from ..simulator import Simulator

#: Signs of the changes to tank contents by kind of propellant flow.
_SIGNS = {
    PropellantFlowKind.LOADED: 1,
    PropellantFlowKind.ADDED: 1,
    PropellantFlowKind.TRANSFER_IN: 1,
    PropellantFlowKind.TRANSFER_OUT: -1,
    PropellantFlowKind.TRANSFER_LOSS: -1,
    PropellantFlowKind.BURNED: -1,
    PropellantFlowKind.BOILOFF: -1,
    PropellantFlowKind.CONSUMED: -1,
}


class TankHistory(CamelModel):
    """
    Contents of an integral tank of a vehicle over time.
    """

    vehicle_id: UUID = Field(..., description="Vehicle unique identifier")
    vehicle_name: str = Field(..., description="Vehicle name")
    tank: str = Field(..., description="Tank key, e.g., OMS Fuel")
    role: str = Field("Fuel", description="Tank role (Fuel or Oxidizer)")
    resource: Optional[str] = Field(None, description="Contained resource name")
    unit_mass: float = Field(1.0, description="Unit mass (kg) of the resource")
    max_amount: float = Field(0.0, description="Capacity (units)")
    points: List[Tuple[float, float]] = Field(
        [],
        description="(time (days), amount (units)) points, linear between "
        "points (boiloff) and with two points at the time of instantaneous "
        "changes",
    )


class BurnRecord(CamelModel):
    """
    Propellant burned from a tank by one burn.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    event: Optional[str] = Field(None, description="Burn event name")
    amount: float = Field(0.0, description="Amount (units) burned")


class PropellantBudget(CamelModel):
    """
    Sources and uses of the contents of an integral tank of a vehicle. The
    budget closes: loaded + added + transferred in - transferred out -
    transfer loss - burned - boiloff - consumed = residual.
    """

    vehicle_id: UUID = Field(..., description="Vehicle unique identifier")
    vehicle_name: str = Field(..., description="Vehicle name")
    tank: str = Field(..., description="Tank key, e.g., OMS Fuel")
    role: str = Field("Fuel", description="Tank role (Fuel or Oxidizer)")
    resource: Optional[str] = Field(None, description="Contained resource name")
    unit_mass: float = Field(1.0, description="Unit mass (kg) of the resource")
    max_amount: float = Field(0.0, description="Capacity (units)")
    loaded: float = Field(0.0, description="Initial contents (units)")
    added: float = Field(0.0, description="Amount added by events (units)")
    transferred_in: float = Field(0.0, description="Amount received (units)")
    transferred_out: float = Field(0.0, description="Amount sent and received (units)")
    transfer_loss: float = Field(0.0, description="Amount lost in transfers (units)")
    burned: float = Field(0.0, description="Amount burned (units)")
    boiloff: float = Field(0.0, description="Amount lost to boiloff (units)")
    consumed: float = Field(
        0.0, description="Amount consumed (or produced, if negative) by demands (units)"
    )
    residual: float = Field(0.0, description="Final contents (units)")
    burns: List[BurnRecord] = Field([], description="Propellant burned by each burn")


class PropellantTotals(CamelModel):
    """
    Total propellant flows (kg) over all vehicle tanks.
    """

    loaded_mass: float = Field(0.0, description="Initial contents (kg)")
    transferred_mass: float = Field(0.0, description="Mass transferred (kg)")
    transfer_loss_mass: float = Field(0.0, description="Mass lost in transfers (kg)")
    burned_mass: float = Field(0.0, description="Mass burned (kg)")
    boiloff_mass: float = Field(0.0, description="Mass lost to boiloff (kg)")


class FlowLink(CamelModel):
    """
    A flow of a resource (in mass) between two nodes of the propellant
    logistics network: vehicle groups (vehicles of the same name in all
    missions, e.g., "Tanker"), sources (loaded, added, and produced
    propellant), and sinks (burned, boiloff, transfer losses, consumed, and
    residual propellant).
    """

    source: str = Field(..., description="Source node")
    target: str = Field(..., description="Target node")
    resource: str = Field(..., description="Resource name")
    mass: float = Field(0.0, description="Mass (kg)")


#: Source and sink nodes of the propellant logistics network.
LOADED, ADDED, PRODUCED = "Loaded", "Added", "Produced"
BURNED, BOILOFF, LOSS, CONSUMED, RESIDUAL = (
    "Burned",
    "Boiloff",
    "Transfer Loss",
    "Consumed",
    "Residual",
)


#: Source of the changes which add to a tank (unless from a counterpart).
_SOURCES = {
    PropellantFlowKind.LOADED: LOADED,
    PropellantFlowKind.ADDED: ADDED,
    PropellantFlowKind.TRANSFER_IN: ADDED,
}
#: Sink of the changes which remove from a tank.
_SINKS = {
    PropellantFlowKind.TRANSFER_LOSS: LOSS,
    PropellantFlowKind.BURNED: BURNED,
    PropellantFlowKind.BOILOFF: BOILOFF,
}


def vehicle_group(name: str) -> str:
    """
    Groups an element by its name without a mission prefix ("Mission | ") or
    a trailing number, e.g., "Artemis III | Tanker 12" is a "Tanker".
    """
    name = name.rsplit(" | ", 1)[-1]
    return re.sub(r"\s+\d+$", "", name) or name


def flow_links(flows: List[PropellantFlow]) -> List[FlowLink]:
    """
    Aggregates the changes to the contents of vehicle tanks to the flows of
    each resource between vehicle groups, sources, and sinks. The flows into
    and out of each vehicle group balance.

    Args:
        flows ([:obj:`PropellantFlow`]): The changes to tank contents.

    Returns:
        [:obj:`FlowLink`]: The flows (largest first).
    """
    vehicles = {flow.vehicle_name for flow in flows}
    masses: Dict[Tuple[str, str, str], float] = {}
    residual: Dict[Tuple[UUID, str], PropellantFlow] = {}

    def add(source, target, resource, mass):
        if source != target and mass > 0:
            key = (source, target, resource)
            masses[key] = masses.get(key, 0.0) + mass

    for flow in flows:
        if flow.resource_name is None:
            continue
        group = vehicle_group(flow.vehicle_name)
        resource = flow.resource_name
        mass = flow.amount * flow.unit_mass
        other = vehicle_group(flow.counterpart) if flow.counterpart else None
        residual[(flow.vehicle_id, flow.tank_key)] = flow
        if flow.kind in _SOURCES:
            add(other or _SOURCES[flow.kind], group, resource, mass)
        elif flow.kind in _SINKS:
            add(group, _SINKS[flow.kind], resource, mass)
        elif flow.kind == PropellantFlowKind.TRANSFER_OUT:
            # transfers between vehicles are counted where they are received
            if flow.counterpart not in vehicles:
                add(group, other or CONSUMED, resource, mass)
        elif flow.kind == PropellantFlowKind.CONSUMED:
            if mass >= 0:
                add(group, other or CONSUMED, resource, mass)
            else:
                add(other or PRODUCED, group, resource, -mass)
    for flow in residual.values():
        add(
            vehicle_group(flow.vehicle_name),
            RESIDUAL,
            flow.resource_name,
            flow.amount_after * flow.unit_mass,
        )
    return [
        FlowLink(source=source, target=target, resource=resource, mass=mass)
        for (source, target, resource), mass in sorted(
            masses.items(), key=lambda item: -item[1]
        )
    ]


class PropellantAnalysis(CamelModel):
    """
    Contents of the integral tanks of all vehicles over time with propellant
    budgets.
    """

    tanks: List[TankHistory] = Field([], description="Tank contents over time")
    budgets: List[PropellantBudget] = Field([], description="Tank budgets")
    totals: PropellantTotals = Field(
        PropellantTotals(), description="Total propellant flows"
    )
    links: List[FlowLink] = Field(
        [], description="Flows between vehicle groups, sources, and sinks"
    )

    @classmethod
    def create(cls, simulator: Simulator) -> "PropellantAnalysis":
        """
        Creates the propellant analysis of an executed simulator.

        Args:
            simulator (:obj:`Simulator`): The executed simulator.

        Returns:
            :obj:`PropellantAnalysis`: The analysis.
        """
        histories: Dict[Tuple[UUID, str], TankHistory] = {}
        budgets: Dict[Tuple[UUID, str], PropellantBudget] = {}
        last: Dict[Tuple[UUID, str], float] = {}
        totals = PropellantTotals()
        for flow in simulator.propellant_flows:
            key = (flow.vehicle_id, flow.tank_key)
            if key not in histories:
                info = _tank_info(flow)
                histories[key] = TankHistory(**info)
                budgets[key] = PropellantBudget(**info)
                last[key] = 0.0
            history = histories[key]
            budget = budgets[key]
            if flow.resource_name is not None:
                history.resource = budget.resource = flow.resource_name
                history.unit_mass = budget.unit_mass = flow.unit_mass
            if flow.kind != PropellantFlowKind.BOILOFF and (
                not history.points or history.points[-1] != (flow.time, last[key])
            ):
                history.points.append((flow.time, last[key]))
            history.points.append((flow.time, flow.amount_after))
            last[key] = flow.amount_after
            budget.residual = flow.amount_after
            _add_flow(budget, totals, flow)
        end_time = simulator.time
        registrar = simulator.state.network.registrar if simulator.state else {}
        for key, history in histories.items():
            if key[0] in registrar and history.points[-1][0] < end_time:
                history.points.append((end_time, last[key]))
        return cls(
            tanks=list(histories.values()),
            budgets=list(budgets.values()),
            totals=totals,
            links=flow_links(simulator.propellant_flows),
        )


def _tank_info(flow: PropellantFlow) -> dict:
    return {
        "vehicle_id": flow.vehicle_id,
        "vehicle_name": flow.vehicle_name,
        "tank": flow.tank_key,
        "role": flow.tank_role,
        "resource": flow.resource_name,
        "unit_mass": flow.unit_mass,
        "max_amount": flow.max_amount,
    }


def _add_flow(budget: PropellantBudget, totals: PropellantTotals, flow: PropellantFlow):
    mass = flow.amount * flow.unit_mass
    if flow.kind == PropellantFlowKind.LOADED:
        budget.loaded += flow.amount
        totals.loaded_mass += mass
    elif flow.kind == PropellantFlowKind.ADDED:
        budget.added += flow.amount
    elif flow.kind == PropellantFlowKind.TRANSFER_IN:
        budget.transferred_in += flow.amount
        totals.transferred_mass += mass
    elif flow.kind == PropellantFlowKind.TRANSFER_OUT:
        budget.transferred_out += flow.amount
    elif flow.kind == PropellantFlowKind.TRANSFER_LOSS:
        budget.transfer_loss += flow.amount
        totals.transfer_loss_mass += mass
    elif flow.kind == PropellantFlowKind.BURNED:
        budget.burned += flow.amount
        totals.burned_mass += mass
        budget.burns.append(
            BurnRecord(time=flow.time, event=flow.event_name, amount=flow.amount)
        )
    elif flow.kind == PropellantFlowKind.BOILOFF:
        budget.boiloff += flow.amount
        totals.boiloff_mass += mass
    elif flow.kind == PropellantFlowKind.CONSUMED:
        budget.consumed += flow.amount


# ---------------------------------------------------------------- tankers


class TankerSizingRequest(CamelModel):
    """
    Parameters of a campaign of tanker flights which aggregate propellant in
    a depot before a vehicle departs with (or is refueled from) it.
    """

    required: float = Field(
        ..., description="Propellant mass (kg) required in the depot at departure", ge=0
    )
    tanker_delivery: float = Field(
        ..., description="Propellant mass (kg) offloaded by each tanker flight", gt=0
    )
    depot_capacity: Optional[float] = Field(
        None,
        description="Depot propellant capacity (kg) (default: the required mass)",
        gt=0,
    )
    initial: float = Field(
        0.0,
        description="Propellant mass (kg) in the depot before the first flight",
        ge=0,
    )
    boiloff_rate: float = Field(
        0.0, description="Fraction of the depot capacity lost per day", ge=0, le=1
    )
    interval_days: float = Field(
        0.0, description="Time (days) between tanker flights", ge=0
    )
    loiter_days: float = Field(
        0.0, description="Time (days) between the last flight and departure", ge=0
    )
    transfer_loss: float = Field(
        0.0, description="Fraction of each offload lost in transfer", ge=0, lt=1
    )
    max_flights: int = Field(
        50, description="Maximum number of tanker flights considered", ge=0, le=1000
    )


class TankerSizing(CamelModel):
    """
    Number of tanker flights required to aggregate propellant in a depot.
    """

    flights: Optional[int] = Field(
        None, description="Number of tanker flights required (None if infeasible)"
    )
    feasible: bool = Field(False, description="True, if the required mass is met")
    reason: Optional[str] = Field(None, description="Reason if infeasible")
    final: float = Field(0.0, description="Depot propellant mass (kg) at departure")
    delivered: float = Field(0.0, description="Propellant mass (kg) received")
    boiloff: float = Field(0.0, description="Propellant mass (kg) lost to boiloff")
    transfer_loss: float = Field(
        0.0, description="Propellant mass (kg) lost in transfer"
    )
    spilled: float = Field(
        0.0, description="Offloaded propellant mass (kg) which exceeded the capacity"
    )
    timeline: List[Tuple[float, float]] = Field(
        [], description="(time (days), depot propellant mass (kg)) points"
    )


def size_tankers(request: TankerSizingRequest) -> TankerSizing:
    """
    Sizes a tanker campaign by simulating the depot contents for an
    increasing number of tanker flights until the required propellant mass
    remains at departure. The depot loses a constant fraction of its capacity
    per day to boiloff (see :class:`~spacenet.simulation.elements.SimResourceTank`).

    Args:
        request (:obj:`TankerSizingRequest`): The campaign parameters.

    Returns:
        :obj:`TankerSizing`: The number of flights and depot timeline.
    """
    capacity = request.depot_capacity or request.required
    daily_loss = request.boiloff_rate * capacity
    received = request.tanker_delivery * (1 - request.transfer_loss)
    if capacity < request.required:
        return TankerSizing(
            feasible=False,
            reason="The depot capacity is less than the required propellant mass.",
        )
    state = _DepotState(min(request.initial, capacity), daily_loss)
    for flights in range(0, request.max_flights + 1):
        if flights > 0:
            if flights > 1:
                state.elapse(request.interval_days)
            state.receive(received, request.tanker_delivery, capacity)
        final, _ = state.after(request.loiter_days)
        if final >= request.required - 1e-9:
            state.elapse(request.loiter_days)
            return state.result(flights, True, None)
        if flights > 0 and received <= daily_loss * request.interval_days:
            return state.result(
                None,
                False,
                "Each tanker flight delivers no more propellant than boils off "
                "between flights.",
            )
    state.elapse(request.loiter_days)
    return state.result(
        None, False, f"More than {request.max_flights} tanker flights are required."
    )


class _DepotState:
    """Simulated contents of a depot during a tanker campaign."""

    def __init__(self, amount: float, daily_loss: float):
        self.time = 0.0
        self.amount = amount
        self.daily_loss = daily_loss
        self.delivered = 0.0
        self.boiloff = 0.0
        self.transfer_loss = 0.0
        self.spilled = 0.0
        self.timeline: List[Tuple[float, float]] = [(0.0, amount)]

    def after(self, days: float) -> Tuple[float, float]:
        """Gets the (amount, loss) after a duration without changing state."""
        loss = min(self.amount, self.daily_loss * days)
        return self.amount - loss, loss

    def elapse(self, days: float):
        """Elapses a duration with boiloff."""
        if days <= 0:
            return
        self.amount, loss = self.after(days)
        self.boiloff += loss
        self.time += days
        self.timeline.append((self.time, self.amount))

    def receive(self, received: float, offloaded: float, capacity: float):
        """Receives one tanker offload (limited by the capacity)."""
        accepted = min(received, capacity - self.amount)
        self.spilled += received - accepted
        self.transfer_loss += offloaded - received
        self.delivered += accepted
        self.amount += accepted
        self.timeline.append((self.time, self.amount))

    def result(self, flights, feasible, reason) -> TankerSizing:
        """Creates the sizing result."""
        return TankerSizing(
            flights=flights,
            feasible=feasible,
            reason=reason,
            final=self.amount,
            delivered=self.delivered,
            boiloff=self.boiloff,
            transfer_loss=self.transfer_loss,
            spilled=self.spilled,
            timeline=self.timeline,
        )


def closed_form_flights(request: TankerSizingRequest) -> float:
    """
    Gets the (fractional) number of flights required without capacity limits
    or boiloff clamping, as a check of :func:`size_tankers`:
    n = (required + loss * ((n - 1) * interval + loiter) - initial) / received.

    Args:
        request (:obj:`TankerSizingRequest`): The campaign parameters.

    Returns:
        float: The fractional number of flights (infinite if infeasible).
    """
    capacity = request.depot_capacity or request.required
    daily_loss = request.boiloff_rate * capacity
    received = request.tanker_delivery * (1 - request.transfer_loss)
    net = received - daily_loss * request.interval_days
    if net <= 0:
        return math.inf
    return (
        request.required
        - request.initial
        + daily_loss * (request.loiter_days - request.interval_days)
    ) / net
