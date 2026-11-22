"""
Object schemas for the results of a full simulation.
"""

from typing import Dict, Iterator, List, Optional, Tuple
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ...schemas import Scenario
from ..records import (
    ElementInfo,
    ElementRecord,
    ElementSnapshot,
    NetworkHistory,
    TankInfo,
)
from ..simulator import FullSimulator
from .issues import SimIssue, collect_issues
from .missions import LocationSummary
from .cost import CostAnalysis
from .isru import ISRUAnalysis
from .power import PowerAnalysis
from .propellant import PropellantAnalysis
from .state import ElementState


class MeasureTotals(CamelModel):
    """
    Total measures of effectiveness of a scenario.
    """

    crew_surface_days: float = Field(0.0, description="Crew surface days (crew-days)")
    crew_time: float = Field(0.0, description="Crew time (crew-hours)")
    exploration_capability: float = Field(
        0.0, description="Exploration capability (kg-crew-days)"
    )
    exploration_mass_delivered: float = Field(
        0.0, description="Exploration mass delivered (kg)"
    )
    launch_mass: float = Field(0.0, description="Mass (kg) launched from Earth")
    up_mass_capacity_utilization: float = Field(
        0.0, description="Fraction of cargo capacity used by transports from Earth"
    )
    down_mass_capacity_utilization: float = Field(
        0.0, description="Fraction of cargo capacity used by transports to Earth"
    )
    relative_exploration_capability: float = Field(
        0.0,
        description="Exploration capability per launch mass relative to Apollo 17",
    )
    propellant_burned_mass: float = Field(
        0.0, description="Propellant mass (kg) burned by vehicles"
    )
    propellant_boiloff_mass: float = Field(
        0.0, description="Propellant mass (kg) lost to boiloff"
    )
    propellant_transfer_loss_mass: float = Field(
        0.0, description="Propellant mass (kg) lost in transfers"
    )
    energy_deficit: float = Field(
        0.0, description="Electrical energy (kWh) which could not be supplied"
    )
    campaign_cost: float = Field(
        0.0,
        description="Cost (millions of US dollars) of costed elements and transports",
    )
    isru_output_mass: float = Field(
        0.0, description="Mass (kg) of resources produced by ISRU processes"
    )
    isru_energy: float = Field(
        0.0, description="Electrical energy (kWh) consumed by ISRU processes"
    )
    landed_mass: float = Field(
        0.0, description="Mass (kg) landed on the surface of bodies other than Earth"
    )
    launch_mass_per_landed_mass: float = Field(
        0.0, description="Mass launched from Earth per mass landed (kg/kg)"
    )
    crew_days: float = Field(
        0.0, description="Crew-days away from the surface of Earth"
    )
    logistics_mass: float = Field(
        0.0, description="Mass (kg) of resources demanded away from Earth"
    )
    logistics_mass_per_crew_day: float = Field(
        0.0, description="Logistics mass (kg) per crew-day away from Earth"
    )
    consumption_mass: float = Field(
        0.0,
        description="Mass (kg) of resources consumed or burned away from Earth",
    )
    in_situ_consumption_mass: float = Field(
        0.0,
        description="Mass (kg) of resources consumed or burned away from Earth "
        "which was produced in situ",
    )
    earth_independence: float = Field(
        0.0,
        description="Fraction of the mass consumed away from Earth produced in situ",
    )
    min_days_of_supply: Optional[float] = Field(
        None,
        description="Fewest days of supply on hand at any location with "
        "continuous demands",
    )

    @classmethod
    def create(
        cls,
        simulator: FullSimulator,
        propellant: Optional["PropellantAnalysis"] = None,
        power: Optional["PowerAnalysis"] = None,
        cost: Optional["CostAnalysis"] = None,
        isru: Optional["ISRUAnalysis"] = None,
    ) -> "MeasureTotals":
        """
        Creates the total measures of effectiveness of an executed simulator.

        Args:
            simulator (:obj:`FullSimulator`): The executed simulator.
            propellant (:obj:`PropellantAnalysis`): The propellant analysis
                (default: created from the simulator).
            power (:obj:`PowerAnalysis`): The power analysis (default: created).
            cost (:obj:`CostAnalysis`): The cost analysis (default: created).
            isru (:obj:`ISRUAnalysis`): The ISRU analysis (default: created).

        Returns:
            :obj:`MeasureTotals`: The totals.
        """
        propellant = propellant or PropellantAnalysis.create(simulator)
        power = power or PowerAnalysis.create(simulator)
        cost = cost or CostAnalysis.create(simulator, simulator.scenario.start_date)
        isru = isru or ISRUAnalysis.create(simulator)
        return cls(
            crew_surface_days=simulator.total_crew_surface_days,
            crew_time=simulator.total_crew_time,
            exploration_capability=simulator.total_exploration_capability,
            exploration_mass_delivered=simulator.total_exploration_mass_delivered,
            launch_mass=simulator.total_launch_mass,
            up_mass_capacity_utilization=simulator.total_up_mass_capacity_utilization,
            down_mass_capacity_utilization=simulator.total_down_mass_capacity_utilization,
            relative_exploration_capability=simulator.total_relative_exploration_capability,
            propellant_burned_mass=propellant.totals.burned_mass,
            propellant_boiloff_mass=propellant.totals.boiloff_mass,
            propellant_transfer_loss_mass=propellant.totals.transfer_loss_mass,
            energy_deficit=power.total_deficit,
            campaign_cost=cost.total,
            isru_output_mass=isru.total_output_mass,
            isru_energy=isru.total_energy,
            landed_mass=simulator.total_landed_mass,
            launch_mass_per_landed_mass=simulator.total_launch_mass_per_landed_mass,
            crew_days=simulator.total_crew_days,
            logistics_mass=simulator.total_logistics_mass,
            logistics_mass_per_crew_day=simulator.total_logistics_mass_per_crew_day,
            consumption_mass=simulator.total_consumption,
            in_situ_consumption_mass=simulator.total_in_situ_consumption,
            earth_independence=simulator.total_earth_independence,
            min_days_of_supply=simulator.min_days_of_supply,
        )


class MeasureRecord(CamelModel):
    """
    One record of a measure of effectiveness.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    location: Optional[UUID] = Field(None, description="Location unique identifier")
    amount: float = Field(0.0, description="Amount of the measure")
    type: Optional[str] = Field(
        None,
        description="Category (crew time), source (consumption), or limiting "
        "resource (days of supply)",
    )
    capacity: Optional[float] = Field(
        None, description="Capacity (kg) (capacity utilization)"
    )


def _records(history, amount=lambda m: m.amount) -> List[MeasureRecord]:
    return [
        MeasureRecord(
            time=m.time,
            location=None if m.location is None else m.location.id,
            amount=amount(m),
            type=getattr(m, "type", None),
            capacity=getattr(m, "capacity", None),
        )
        for m in history
    ]


class Measures(CamelModel):
    """
    Histories of the measures of effectiveness of a scenario.
    """

    crew_surface_days: List[MeasureRecord] = []
    crew_time: List[MeasureRecord] = []
    exploration_capability: List[MeasureRecord] = []
    exploration_mass_delivered: List[MeasureRecord] = []
    launch_mass: List[MeasureRecord] = []
    up_mass_capacity_utilization: List[MeasureRecord] = []
    down_mass_capacity_utilization: List[MeasureRecord] = []
    landed_mass: List[MeasureRecord] = []
    crew_days: List[MeasureRecord] = []
    logistics_mass: List[MeasureRecord] = []
    consumption: List[MeasureRecord] = Field(
        [], description="Mass (kg) consumed away from Earth by source"
    )
    days_of_supply: List[MeasureRecord] = Field(
        [],
        description="Days of supply on hand (not cumulative) by limiting resource",
    )


class NetworkState(CamelModel):
    """
    Elements at each network location at a point in time.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    locations: Dict[UUID, List[ElementState]] = Field(
        {}, description="Top-level elements by location unique identifier"
    )


class MassSeries(CamelModel):
    """
    Mass of one class of supply over time.
    """

    class_of_supply: int = Field(..., description="Top-level class of supply")
    points: List[List[float]] = Field(
        [], description="Pairs of time (days) and mass (kg)"
    )


class MassHistory(CamelModel):
    """
    Mass by class of supply of a location or an element over time.
    """

    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    type: Optional[str] = Field(None, description="Element type")
    series: List[MassSeries] = Field([], description="Mass by class of supply")


def _add_point(history: Dict[int, List[List[float]]], times: int, masses: Dict):
    """Adds the masses at one time, padding classes of supply first seen later."""
    for class_of_supply in set(history) | set(masses):
        points = history.setdefault(class_of_supply, [0.0] * times)
        points.append(masses.get(class_of_supply, 0.0))


def _to_series(times: List[float], history: Dict[int, List[float]]) -> List[MassSeries]:
    return [
        MassSeries(
            class_of_supply=class_of_supply,
            points=[[t, m] for t, m in zip(times, masses)],
        )
        for class_of_supply, masses in sorted(history.items())
    ]


class TankInfoState(CamelModel):
    """
    Static information about an integral tank of a vehicle.
    """

    label: str = Field(..., description="Label, e.g., OMS/RCS Fuel")
    key: Optional[str] = Field(None, description="Tank key, e.g., OMS Fuel")
    role: str = Field("Fuel", description="Tank role (Fuel or Oxidizer)")
    max_amount: float = Field(0.0, description="Capacity (units)")
    propulsion: Dict[str, float] = Field(
        {}, description="Specific impulse (s) of each system which burns from the tank"
    )
    boiloff_rate: float = Field(
        0.0, description="Fraction of the capacity lost per day"
    )


class ElementInfoState(CamelModel):
    """
    Static information about an element (recorded once per simulation).
    """

    id: UUID
    name: str
    type: Optional[str] = None
    template_id: Optional[UUID] = None
    icon: Optional[str] = None
    class_of_supply: int = 0
    environment: Optional[str] = None
    cargo_environment: Optional[str] = None
    is_carrier: bool = False
    is_crew: bool = False
    is_container: bool = False
    max_cargo_mass: float = 0.0
    max_cargo_volume: float = 0.0
    max_crew_size: int = 0
    states: List[str] = []
    state_types: List[str] = []
    isp: float = 0.0
    fuel_tanks: List[TankInfoState] = []
    energy_capacity: float = Field(0.0, description="Energy storage capacity (kWh)")


class ElementChange(CamelModel):
    """
    Dynamic state of an element which was created or changed at a time step.
    """

    element: int = Field(..., description="Index of the element (history elements)")
    location: Optional[int] = Field(
        None, description="Index of the location (top-level elements)"
    )
    container: Optional[int] = Field(
        None, description="Index of the carrier element (nested elements)"
    )
    state_index: int = -1
    mass: float = 0.0
    total_mass: float = 0.0
    volume: float = 0.0
    cargo_mass: float = 0.0
    cargo_volume: float = 0.0
    crew_size: int = 0
    resources: Dict[str, float] = Field(
        {}, description="Resource amounts of a resource container"
    )
    fuel_names: List[Optional[str]] = Field(
        [], description="Resource name of each integral tank"
    )
    fuel_amounts: List[float] = Field([], description="Amount of each integral tank")
    mass_by_class_of_supply: Dict[int, float] = {}
    energy: float = Field(0.0, description="Stored electrical energy (kWh)")


class HistoryStep(CamelModel):
    """
    Changes to the elements of the network at one time step.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    changes: List[ElementChange] = Field(
        [], description="Elements created or changed since the previous time step"
    )
    removed: List[int] = Field(
        [], description="Indices of the elements removed since the previous time step"
    )


class SimulationHistory(CamelModel):
    """
    History of the elements of the network: static information about each
    element (ordered as within containers) and the changes at each time step.
    """

    elements: List[ElementInfoState] = Field([], description="Element information")
    frames: List[HistoryStep] = Field([], description="Changes at each time step")

    @classmethod
    def create(
        cls, history: NetworkHistory, location_ids: List[UUID]
    ) -> "SimulationHistory":
        """
        Creates the history from the recorded history of a simulator.

        Args:
            history (:obj:`NetworkHistory`): The recorded history.
            location_ids ([UUID]): The unique identifiers of the locations
                (indexed by element changes).

        Returns:
            :obj:`SimulationHistory`: The history.
        """
        infos = sorted(history.elements.values(), key=lambda i: i.sort_key)
        elements = {info.id: index for index, info in enumerate(infos)}
        locations = {
            location_id: index for index, location_id in enumerate(location_ids)
        }

        def change(element_id: UUID, record: ElementRecord) -> ElementChange:
            return ElementChange(
                element=elements[element_id],
                location=locations.get(record.container_id),
                container=elements.get(record.container_id),
                state_index=record.state_index,
                mass=record.mass,
                total_mass=record.total_mass,
                volume=record.volume,
                cargo_mass=record.cargo_mass,
                cargo_volume=record.cargo_volume,
                crew_size=record.crew_size,
                resources=dict(record.resources),
                fuel_names=[name for name, _ in record.tanks],
                fuel_amounts=[amount for _, amount in record.tanks],
                mass_by_class_of_supply=dict(record.mass_by_class_of_supply),
                energy=record.energy,
            )

        return cls(
            elements=[
                ElementInfoState(
                    id=info.id,
                    name=info.name,
                    type=info.type,
                    template_id=info.template_id,
                    icon=info.icon,
                    class_of_supply=info.class_of_supply,
                    environment=info.environment,
                    cargo_environment=info.cargo_environment,
                    is_carrier=info.is_carrier,
                    is_crew=info.is_crew,
                    is_container=info.is_container,
                    max_cargo_mass=info.max_cargo_mass,
                    max_cargo_volume=info.max_cargo_volume,
                    max_crew_size=info.max_crew_size,
                    states=list(info.states),
                    state_types=list(info.state_types),
                    isp=info.isp,
                    energy_capacity=info.energy_capacity,
                    fuel_tanks=[
                        TankInfoState(
                            label=tank.label,
                            key=tank.key,
                            role=tank.role,
                            max_amount=tank.max_amount,
                            propulsion=dict(tank.propulsion),
                            boiloff_rate=tank.boiloff_rate,
                        )
                        for tank in info.tanks
                    ],
                )
                for info in infos
            ],
            frames=[
                HistoryStep(
                    time=frame.time,
                    changes=sorted(
                        (change(i, r) for i, r in frame.changed.items()),
                        key=lambda c: c.element,
                    ),
                    removed=sorted(elements[i] for i in frame.removed),
                )
                for frame in history.frames
            ],
        )

    def states(self) -> Iterator[Dict[int, ElementChange]]:
        """
        Iterates over the time steps.

        Yields:
            {int: :obj:`ElementChange`}: The state of each existing element
            by element index (the dictionary is reused).
        """
        state: Dict[int, ElementChange] = {}
        for frame in self.frames:
            for element in frame.removed:
                state.pop(element, None)
            for change in frame.changes:
                state[change.element] = change
            yield state

    def element_state(
        self, change: ElementChange, contents: List[ElementState]
    ) -> ElementState:
        """Composes the state of an element from its information and change."""
        info = self.elements[change.element]
        record = ElementRecord(
            container_id=None,
            state_index=change.state_index,
            mass=change.mass,
            total_mass=change.total_mass,
            volume=change.volume,
            cargo_mass=change.cargo_mass,
            cargo_volume=change.cargo_volume,
            crew_size=change.crew_size,
            resources=tuple(change.resources.items()),
            tanks=tuple(zip(change.fuel_names, change.fuel_amounts)),
            mass_by_class_of_supply=tuple(change.mass_by_class_of_supply.items()),
            energy=change.energy,
        )
        snapshot = ElementSnapshot.compose(
            ElementInfo(
                id=info.id,
                name=info.name,
                type=info.type,
                class_of_supply=info.class_of_supply,
                environment=info.environment,
                cargo_environment=info.cargo_environment,
                is_carrier=info.is_carrier,
                is_crew=info.is_crew,
                is_container=info.is_container,
                max_cargo_mass=info.max_cargo_mass,
                max_cargo_volume=info.max_cargo_volume,
                max_crew_size=info.max_crew_size,
                states=tuple(info.states),
                state_types=tuple(info.state_types),
                isp=info.isp,
                template_id=info.template_id,
                icon=info.icon,
                tanks=tuple(
                    TankInfo(
                        label=t.label,
                        key=t.key,
                        role=t.role,
                        max_amount=t.max_amount,
                        propulsion=tuple(t.propulsion.items()),
                        boiloff_rate=t.boiloff_rate,
                    )
                    for t in info.fuel_tanks
                ),
                sort_key=(),
                energy_capacity=info.energy_capacity,
            ),
            record,
        )
        state = ElementState.from_snapshot(snapshot)
        state.contents = contents
        return state

    def network_states(self, location_ids: List[UUID]) -> Iterator[NetworkState]:
        """
        Iterates over the elements at each location at each time step.

        Args:
            location_ids ([UUID]): The unique identifiers of the locations
                (indexed by element changes).

        Yields:
            :obj:`NetworkState`: The elements at each location.
        """
        for frame, state in zip(self.frames, self.states()):
            yield NetworkState(
                time=frame.time, locations=self._compose(state, location_ids)
            )

    def _compose(
        self, state: Dict[int, ElementChange], location_ids: List[UUID]
    ) -> Dict[UUID, List[ElementState]]:
        """Composes the top-level element states at each location."""
        children: Dict[Tuple[str, int], List[int]] = {}
        for element in sorted(state):
            change = state[element]
            parent = (
                ("location", change.location)
                if change.location is not None
                else ("element", change.container)
            )
            children.setdefault(parent, []).append(element)

        def create(element: int) -> ElementState:
            return self.element_state(
                state[element],
                [create(c) for c in children.get(("element", element), [])],
            )

        return {
            location_id: [create(e) for e in children.get(("location", index), [])]
            for index, location_id in enumerate(location_ids)
        }


def _aggregate(records: List[MeasureRecord]) -> List[MeasureRecord]:
    """Sums the records with the same time, location, and type."""
    totals: Dict[tuple, MeasureRecord] = {}
    for record in records:
        key = (record.time, record.location, record.type)
        if key in totals:
            totals[key].amount += record.amount
        else:
            totals[key] = record.model_copy()
    return list(totals.values())


class SimulationAnalysis(CamelModel):
    """
    Results of a full simulation of a scenario.
    """

    issues: List[SimIssue] = Field([], description="Errors and warnings")
    error_count: int = Field(0, description="Number of events which failed")
    unsatisfied_demand_count: int = Field(
        0, description="Number of demands which could not be satisfied"
    )
    end_time: float = Field(
        0.0,
        description="Time (days) of the scenario end (default: the last event)",
    )
    totals: MeasureTotals = Field(
        MeasureTotals(), description="Total measures of effectiveness"
    )
    measures: Measures = Field(
        Measures(), description="Histories of the measures of effectiveness"
    )
    locations: List[LocationSummary] = Field([], description="Network locations")
    history: SimulationHistory = Field(
        SimulationHistory(),
        description="Elements at each location at each time step (as changes)",
    )
    propellant: PropellantAnalysis = Field(
        PropellantAnalysis(), description="Vehicle tank contents and budgets"
    )
    power: PowerAnalysis = Field(
        PowerAnalysis(), description="Energy balance of each power group"
    )
    cost: CostAnalysis = Field(
        CostAnalysis(), description="Costs of elements and transports"
    )
    isru: ISRUAnalysis = Field(
        ISRUAnalysis(), description="Operation of each ISRU process"
    )

    def network_states(self) -> Iterator[NetworkState]:
        """Iterates over the elements at each location at each time step."""
        location_ids = [location.id for location in self.locations]
        return self.history.network_states(location_ids)

    def network_state(self, index: int) -> NetworkState:
        """Gets the elements at each location at a time step."""
        if index < 0:
            index += len(self.history.frames)
        for position, state in enumerate(self.network_states()):
            if position == index:
                return state
        raise IndexError("time step index out of range")

    def location_masses(self) -> List[MassHistory]:
        """Gets the mass by class of supply at each location over time."""
        times = [frame.time for frame in self.history.frames]
        masses: Dict[int, Dict[int, List[float]]] = {
            i: {} for i in range(len(self.locations))
        }
        for index, state in enumerate(self.history.states()):
            totals: Dict[int, Dict[int, float]] = {}
            for change in state.values():
                if change.location is None:
                    continue
                total = totals.setdefault(change.location, {})
                for key, mass in change.mass_by_class_of_supply.items():
                    total[key] = total.get(key, 0.0) + mass
            for location, history in masses.items():
                _add_point(history, index, totals.get(location, {}))
        return [
            MassHistory(
                id=location.id,
                name=location.name,
                series=_to_series(times, masses[i]),
            )
            for i, location in enumerate(self.locations)
        ]

    def element_masses(self) -> List[MassHistory]:
        """Gets the mass by class of supply of each element over time."""
        times = [frame.time for frame in self.history.frames]
        masses: Dict[int, Dict[int, List[float]]] = {}
        for index, state in enumerate(self.history.states()):
            for element, change in state.items():
                history = masses.setdefault(element, {})
                # pad the time steps before the element existed
                for points in history.values():
                    points.extend([0.0] * (index - len(points)))
                _add_point(history, index, change.mass_by_class_of_supply)
        # pad the time steps after an element was removed
        for history in masses.values():
            for points in history.values():
                points.extend([0.0] * (len(times) - len(points)))
        elements = self.history.elements
        return [
            MassHistory(
                id=elements[i].id,
                name=elements[i].name,
                type=elements[i].type,
                series=_to_series(times, history),
            )
            for i, history in sorted(masses.items(), key=lambda m: elements[m[0]].name)
        ]

    @classmethod
    def create(
        cls, scenario: Scenario, simulator: Optional[FullSimulator] = None
    ) -> "SimulationAnalysis":
        """
        Executes a full simulation of a scenario (including its manifest).

        Args:
            scenario (:obj:`Scenario`): The scenario.
            simulator (:obj:`FullSimulator`): An executed simulator to
                report (default: a new simulator is executed).

        Returns:
            :obj:`SimulationAnalysis`: The analysis results.
        """
        if simulator is None:
            simulator = FullSimulator(scenario)
            simulator.simulate()
        network = simulator.state.network
        propellant = PropellantAnalysis.create(simulator)
        power = PowerAnalysis.create(simulator)
        cost = CostAnalysis.create(simulator, simulator.scenario.start_date)
        isru = ISRUAnalysis.create(simulator)

        return cls(
            issues=collect_issues(simulator),
            error_count=len(simulator.spatial_errors),
            unsatisfied_demand_count=len(simulator.unsatisfied_demands),
            end_time=simulator.time,
            totals=MeasureTotals.create(simulator, propellant, power, cost, isru),
            propellant=propellant,
            power=power,
            cost=cost,
            isru=isru,
            measures=Measures(
                crew_surface_days=_records(simulator.crew_surface_days_history),
                # crew time is recorded for each crew member at each time step
                crew_time=_aggregate(_records(simulator.crew_time_history)),
                exploration_capability=_records(
                    simulator.exploration_capability_history,
                    lambda m: m.mass * m.duration,
                ),
                exploration_mass_delivered=_records(
                    simulator.exploration_mass_delivered_history
                ),
                launch_mass=_records(simulator.launch_mass_history),
                up_mass_capacity_utilization=_records(
                    simulator.up_mass_capacity_utilization_history
                ),
                down_mass_capacity_utilization=_records(
                    simulator.down_mass_capacity_utilization_history
                ),
                landed_mass=_records(simulator.landed_mass_history),
                crew_days=_aggregate(_records(simulator.crew_days_history)),
                logistics_mass=_aggregate(_records(simulator.logistics_mass_history)),
                consumption=_aggregate(_records(simulator.consumption_history)),
                days_of_supply=_records(simulator.days_of_supply_history),
            ),
            locations=[LocationSummary(id=n.id, name=n.name) for n in network.nodes]
            + [
                LocationSummary(id=e.id, name=e.name, is_edge=True)
                for e in network.edges
            ],
            history=SimulationHistory.create(
                simulator.network_history, [l.id for l in network.locations]
            ),
        )
