"""
Object schemas for the simulation state before an event and for the
evaluation of a (draft) event in that state.
"""

from dataclasses import asdict
from typing import Dict, List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ...schemas import AllEvents, Scenario
from ..elements import SimElement
from ..events import (
    LAST_PRIORITY,
    BurnEvent,
    EvaEvent,
    ExplorationProcess,
    FlightTransportEvent,
    SimEvent,
    SpaceTransportEvent,
    TransportEvent,
)
from ..network import SimEdge, SimLocation
from ..records import ElementSnapshot
from ..simulator import PreSimulator
from .issues import SimIssue, collect_issues

SECONDS_PER_DAY = 24 * 60 * 60


class FuelTankState(CamelModel):
    """
    State of an integral fuel tank of a vehicle.
    """

    label: str = Field(..., description="Label, e.g., OMS/RCS Fuel")
    fuel_name: Optional[str] = Field(None, description="Fuel resource name")
    amount: float = Field(0.0, description="Fuel amount (units)")
    max_amount: float = Field(0.0, description="Fuel capacity (units)")
    propulsion: Dict[str, float] = Field(
        {},
        description="Specific impulse (s) of each propulsion system (by "
        "propulsion type) which burns fuel from the tank",
    )
    key: Optional[str] = Field(None, description="Tank key, e.g., OMS Fuel")
    role: str = Field("Fuel", description="Tank role (Fuel or Oxidizer)")
    boiloff_rate: float = Field(
        0.0, description="Fraction of the capacity lost per day"
    )


class ElementState(CamelModel):
    """
    State of an element (and its nested contents) at a point in time.
    """

    id: UUID
    name: str
    type: Optional[str] = None
    state: Optional[str] = None
    mass: float = 0.0
    total_mass: float = 0.0
    volume: float = 0.0
    cargo_mass: float = 0.0
    max_cargo_mass: float = 0.0
    cargo_volume: float = 0.0
    max_cargo_volume: float = 0.0
    crew_size: int = 0
    max_crew_size: int = 0
    is_carrier: bool = False
    is_crew: bool = False
    is_container: bool = False
    resources: Dict[str, float] = {}
    contents: List["ElementState"] = []
    class_of_supply: int = 0
    environment: Optional[str] = None
    cargo_environment: Optional[str] = None
    states: List[str] = []
    state_types: List[str] = []
    state_index: int = -1
    state_type: Optional[str] = None
    fuel_name: Optional[str] = None
    fuel_amount: float = 0.0
    max_fuel_amount: float = 0.0
    isp: float = 0.0
    fuel_tanks: List[FuelTankState] = []
    template_id: Optional[UUID] = None
    icon: Optional[str] = None
    mass_by_class_of_supply: Dict[int, float] = {}

    @classmethod
    def from_snapshot(cls, snapshot: ElementSnapshot) -> "ElementState":
        """Creates an element state from a snapshot."""
        return cls.model_validate(asdict(snapshot))

    @classmethod
    def create(cls, element: SimElement) -> "ElementState":
        """Creates an element state from an element."""
        return cls.from_snapshot(ElementSnapshot.create(element))


class LocationState(CamelModel):
    """
    Elements at a network location at a point in time.
    """

    id: UUID = Field(..., description="Location unique identifier")
    name: str = Field(..., description="Location name")
    is_edge: bool = Field(False, description="True, if the location is an edge")
    elements: List[ElementState] = Field([], description="Top-level elements")

    @classmethod
    def create(cls, location: SimLocation) -> "LocationState":
        """Creates the state of a location."""
        return cls(
            id=location.id,
            name=location.name,
            is_edge=isinstance(location, SimEdge),
            elements=[ElementState.create(e) for e in location.contents],
        )


def _with_event(
    scenario: Scenario,
    mission_index: int,
    event: Optional[AllEvents],
    event_index: Optional[int],
):
    """
    Copies a scenario with an event of a mission inserted (no event index),
    replaced, or removed (no event). Returns the copy and the event index.
    """
    if not 0 <= mission_index < len(scenario.mission_list):
        raise ValueError(f"Invalid mission index {mission_index}")
    mission = scenario.mission_list[mission_index]
    events = list(mission.events)
    if event_index is not None and not 0 <= event_index < len(events):
        raise ValueError(f"Invalid event index {event_index}")
    if event is None:
        if event_index is not None:
            del events[event_index]
    elif event_index is None:
        event_index = len(events)
        events.append(event)
    else:
        events[event_index] = event
    missions = list(scenario.mission_list)
    missions[mission_index] = mission.model_copy(update={"events": events})
    return scenario.model_copy(update={"mission_list": missions}), event_index


class StateAnalysis(CamelModel):
    """
    Simulation state immediately before an event at a time and priority.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    issues: List[SimIssue] = Field(
        [], description="Errors and warnings logged before the event"
    )
    locations: List[LocationState] = Field(
        [], description="Elements at each network location"
    )

    @classmethod
    def create(
        cls,
        scenario: Scenario,
        mission_index: int,
        mission_time: float,
        priority: int,
        exclude_event_index: Optional[int] = None,
    ) -> "StateAnalysis":
        """
        Simulates a scenario up to (but not including) events of a mission
        at a time and priority.

        Args:
            scenario (:obj:`Scenario`): The scenario.
            mission_index (int): The position of the mission in the mission list.
            mission_time (float): The time (days) relative to the mission start.
            priority (int): The priority of coincident events at which to stop.
            exclude_event_index (int): The position of an event of the
                mission to leave out of the simulation (e.g., the event
                being edited).

        Returns:
            :obj:`StateAnalysis`: The simulation state.
        """
        if exclude_event_index is not None:
            scenario, _ = _with_event(
                scenario, mission_index, None, exclude_event_index
            )
        elif not 0 <= mission_index < len(scenario.mission_list):
            raise ValueError(f"Invalid mission index {mission_index}")
        simulator = PreSimulator(scenario)
        simulator.initialize_simulation()
        mission = simulator.state.missions[mission_index]
        time = mission.start_time + simulator.settings.round_time(mission_time)
        simulator.simulate(time, priority, reset=False)
        return cls(
            time=time,
            issues=collect_issues(simulator, demands=False),
            locations=[
                LocationState.create(location)
                for location in simulator.state.network.locations
            ],
        )


class BurnStepResult(CamelModel):
    """
    One action (fire engine or discard element) of an evaluated burn.
    """

    action: str = Field(..., description="Action type (Burn or Stage)")
    element_id: UUID = Field(..., description="Element unique identifier")
    element_name: str = Field(..., description="Element name")
    stack_mass: float = Field(0.0, description="Stack mass (kg) before the action")
    delta_v_achieved: float = Field(0.0, description="Delta-v (m/s) achieved")
    delta_v_remaining: float = Field(
        0.0, description="Delta-v (m/s) still required after the action"
    )
    fuel_used: float = Field(0.0, description="Fuel amount (units) consumed")
    fuel_remaining: float = Field(
        0.0, description="Fuel amount (units) remaining in the vehicle"
    )
    oxidizer_used: Optional[float] = Field(
        None, description="Oxidizer amount (units) consumed (bipropellant systems)"
    )
    oxidizer_remaining: Optional[float] = Field(
        None, description="Oxidizer amount (units) remaining (bipropellant systems)"
    )
    propellant_mass_used: float = Field(
        0.0, description="Total propellant mass (kg) consumed"
    )
    propellant_shortfall: float = Field(
        0.0,
        description="Additional propellant mass (kg) the vehicle would require "
        "to achieve the remaining delta-v",
    )
    message: Optional[str] = Field(None, description="Error which prevented the action")


class TransferStepResult(CamelModel):
    """
    One resource transfer of an evaluated transfer event.
    """

    resource_name: str = Field(..., description="Resource name")
    origin_name: str = Field(..., description="Origin container (or tank) name")
    destination_name: str = Field(
        ..., description="Destination container (or tank) name"
    )
    removed: float = Field(0.0, description="Amount (units) removed from the origin")
    delivered: float = Field(0.0, description="Amount (units) added to the destination")
    lost: float = Field(0.0, description="Amount (units) lost during transfer")
    origin_remaining: float = Field(
        0.0, description="Amount (units) remaining in the origin"
    )
    destination_amount: float = Field(
        0.0, description="Amount (units) in the destination after the transfer"
    )
    destination_space: float = Field(
        0.0, description="Remaining capacity (units) of the destination"
    )


class BurnResult(CamelModel):
    """
    Evaluation of the burn and stage sequence of one burn.
    """

    burn_id: UUID = Field(..., description="Burn unique identifier")
    time: float = Field(0.0, description="Time (days) relative to the scenario start")
    executed: bool = Field(False, description="True, if the burn was executed")
    stack_mass: Optional[float] = Field(
        None, description="Stack mass (kg) at the start of the burn"
    )
    propulsion_type: str = Field(
        "OMS", description="Type of the propulsion systems which perform the burn"
    )
    delta_v_required: float = Field(0.0, description="Required delta-v (m/s)")
    delta_v_achieved: float = Field(0.0, description="Achieved delta-v (m/s)")
    delta_v_remaining: float = Field(0.0, description="Delta-v (m/s) not achieved")
    steps: List[BurnStepResult] = Field([], description="Executed actions")

    @classmethod
    def create(cls, event: BurnEvent) -> "BurnResult":
        """Creates the result of a burn event."""
        required = event.burn.delta_v
        executed = event.delta_v_remaining is not None
        remaining = event.delta_v_remaining if executed else required
        return cls(
            burn_id=event.burn.id,
            propulsion_type=event.burn.propulsion_type.value,
            time=event.time,
            executed=executed,
            stack_mass=event.initial_stack_mass,
            delta_v_required=required,
            delta_v_achieved=required - remaining,
            delta_v_remaining=remaining,
            steps=[BurnStepResult.model_validate(asdict(s)) for s in event.steps],
        )


class TransportResult(CamelModel):
    """
    Evaluation of a transport.
    """

    edge: Optional[UUID] = Field(None, description="Edge unique identifier")
    origin: Optional[UUID] = Field(None, description="Origin node unique identifier")
    destination: Optional[UUID] = Field(
        None, description="Destination node unique identifier"
    )
    duration: Optional[float] = Field(
        None, description="Duration (days), undefined if infinite"
    )
    cargo_mass: Optional[float] = Field(
        None, description="Transported mass (kg) (flight transports)"
    )
    max_cargo_mass: Optional[float] = Field(
        None, description="Mass capacity (kg) (flight transports)"
    )
    crew_size: Optional[int] = Field(
        None, description="Transported crew (flight transports)"
    )
    max_crew_size: Optional[int] = Field(
        None, description="Crew capacity (flight transports)"
    )


class NextEvent(CamelModel):
    """
    Suggested time, priority, and location of an event which follows another.
    """

    mission_time: float = Field(
        ..., description="Time (days) relative to the mission start"
    )
    priority: int = Field(..., description="Priority")
    location: UUID = Field(..., description="Location unique identifier")


def _finite(value: float) -> Optional[float]:
    return value if value is not None and abs(value) != float("inf") else None


class EventEvaluation(CamelModel):
    """
    Evaluation of a (draft) event executed in the simulation state at its
    time and priority.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    issues: List[SimIssue] = Field(
        [], description="Errors and warnings produced by the event"
    )
    burns: List[BurnResult] = Field(
        [], description="Burns of a propulsive burn or space transport"
    )
    transfers: List[TransferStepResult] = Field(
        [], description="Resource transfers of a transfer event"
    )
    transport: Optional[TransportResult] = Field(
        None, description="Transport duration and capacity"
    )
    duration: Optional[float] = Field(
        None, description="Duration (days) of the event, if any"
    )
    container: Optional[ElementState] = Field(
        None,
        description="Carrier or resource container which receives elements or "
        "resources, after the event",
    )
    next: NextEvent = Field(..., description="Suggestion for a following event")

    @classmethod
    def create(
        cls,
        scenario: Scenario,
        mission_index: int,
        event: AllEvents,
        event_index: Optional[int] = None,
    ) -> "EventEvaluation":
        """
        Executes a (draft) event of a mission in the simulation state
        immediately before it. Space transports are simulated until arrival
        to evaluate their burns.

        Args:
            scenario (:obj:`Scenario`): The scenario.
            mission_index (int): The position of the mission in the mission list.
            event (:obj:`AllEvents`): The (draft) event.
            event_index (int): The position of the event it replaces in the
                mission event list (default: the event is added).

        Returns:
            :obj:`EventEvaluation`: The evaluation.
        """
        # pylint: disable=too-many-locals,too-many-branches
        scenario, event_index = _with_event(scenario, mission_index, event, event_index)
        simulator = PreSimulator(scenario)
        simulator.initialize_simulation()
        mission = simulator.state.missions[mission_index]
        sim_event = mission.events[event_index]
        settings = simulator.settings
        mission_time = settings.round_time(sim_event.mission_time or 0.0)
        time = mission.start_time + mission_time
        simulator.simulate(time, sim_event.priority, reset=False)
        # issues before the event are not attributed to it
        prior_errors = len(simulator.spatial_errors)
        prior_warnings = len(simulator.warnings)

        transport = None
        if isinstance(sim_event, TransportEvent) and sim_event.edge is not None:
            transport = TransportResult(
                edge=sim_event.edge.id,
                origin=sim_event.origin.id,
                destination=sim_event.destination.id,
                duration=_finite(sim_event.duration),
            )
            if isinstance(sim_event, FlightTransportEvent):
                mass, crew = sim_event.get_load()
                transport.cargo_mass = mass
                transport.max_cargo_mass = sim_event.edge.max_cargo_mass
                transport.crew_size = crew
                transport.max_crew_size = sim_event.edge.max_crew_size

        sim_event.time = time
        simulator.execute_event(sim_event)
        burn_events: List[BurnEvent] = []
        if isinstance(sim_event, BurnEvent):
            burn_events = [sim_event]
        elif isinstance(sim_event, SpaceTransportEvent):
            burn_events = sorted(
                (
                    e
                    for e in simulator.pending_events
                    if isinstance(e, BurnEvent) and e.root is sim_event
                ),
                key=lambda e: (e.time, e.priority),
            )
            if sim_event.edge is not None:
                simulator.simulate(
                    time + sim_event.edge.duration, LAST_PRIORITY, reset=False
                )

        issues = [
            SimIssue.from_error(e)
            for e in simulator.spatial_errors[prior_errors:]
            if e.event is not None and e.event.root is sim_event
        ]
        issues.extend(
            SimIssue.from_warning(w)
            for w in simulator.warnings[prior_warnings:]
            if w.event is not None and w.event.root is sim_event
        )

        duration = None
        if transport is not None:
            duration = transport.duration
        elif isinstance(sim_event, ExplorationProcess):
            duration = sim_event.duration
        elif isinstance(sim_event, EvaEvent):
            duration = sim_event.eva_duration / 24

        container = None
        for name in ("container", "destination_container"):
            target = getattr(sim_event, name, None)
            if isinstance(target, SimElement):
                container = ElementState.create(target)

        return cls(
            time=time,
            issues=sorted(issues, key=lambda i: i.time),
            burns=[BurnResult.create(e) for e in burn_events],
            transfers=[
                TransferStepResult.model_validate(asdict(r))
                for r in getattr(sim_event, "results", [])
            ],
            transport=transport,
            duration=duration,
            container=container,
            next=_get_next_event(sim_event, mission_time, transport, duration),
        )


def _get_next_event(
    event: SimEvent,
    mission_time: float,
    transport: Optional[TransportResult],
    duration: Optional[float],
) -> NextEvent:
    """Suggests the time, priority, and location of a following event."""
    location = event.location.id
    if transport is not None and transport.duration is not None:
        return NextEvent(
            mission_time=mission_time + transport.duration,
            priority=1,
            location=transport.destination,
        )
    if isinstance(event, ExplorationProcess) and duration is not None:
        return NextEvent(
            mission_time=mission_time + duration, priority=1, location=location
        )
    return NextEvent(
        mission_time=mission_time,
        priority=min(5, max(1, event.priority + 1)),
        location=location,
    )
