"""
Missions used during simulation.
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from .elements import SimCarrier, SimCrewMember, SimElement
from .events import (
    CreateEvent,
    EvaEvent,
    ExplorationProcess,
    FlightTransportEvent,
    SimEvent,
    SpaceTransportEvent,
    TransportEvent,
)
from .network import SimNode
from .resources import DemandSet

if TYPE_CHECKING:  # pragma: no cover
    from .demand_models import SimDemandModel
    from .simulator import Simulator
    from .state import State


class SimMission:
    """
    A mission composed of a sequence of events.
    """

    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(
        self,
        state: "State",
        *,
        name: str,
        start_date: datetime,
        start_time: float,
        index: int = 0,
        origin: Optional[SimNode] = None,
        destination: Optional[SimNode] = None,
        return_origin: Optional[SimNode] = None,
        return_destination: Optional[SimNode] = None,
    ):
        self.state = state
        self.settings = state.settings
        self.name = name
        self.start_date = start_date
        #: Time (days) of the mission start relative to the scenario start.
        self.start_time = start_time
        #: Position in the scenario mission list.
        self.index = index
        self.origin = origin
        self.destination = destination
        self.return_origin = return_origin
        self.return_destination = return_destination
        #: Events with times relative to the mission start.
        self.events: List[SimEvent] = []
        self.demand_models: List["SimDemandModel"] = []
        self._crew_size: Optional[int] = None
        self._crew_members: Optional[List[SimCrewMember]] = None

    def generate_demands(self, simulator: "Simulator") -> DemandSet:
        """
        Generates the mission-level demands.

        Args:
            simulator (:obj:`Simulator`): The simulator.

        Returns:
            :obj:`DemandSet`: The aggregated demands.
        """
        demands = DemandSet()
        for model in self.demand_models:
            if self.settings.time_phased_consumables and hasattr(model, "eva_demands"):
                # other crew consumables are demanded over time (see Simulator)
                demands.add_all(model.eva_demands())
            else:
                demands.add_all(model.generate_demands(self.duration, simulator))
        return demands

    @property
    def crew_members(self) -> List[SimCrewMember]:
        """
        The crew members created in this mission, either directly or inside
        created carriers (identified in the initial state).
        """
        if self._crew_members is None:
            crew = {}
            for element in self.elements:
                if isinstance(element, SimCrewMember):
                    crew[element.id] = element
                elif isinstance(element, SimCarrier):
                    for member in element.complete_contents:
                        if isinstance(member, SimCrewMember):
                            crew[member.id] = member
            self._crew_members = sorted(crew.values(), key=lambda e: e.sort_key)
        return self._crew_members

    def _mission_time(self, event: SimEvent) -> float:
        return self.settings.round_time(event.mission_time or 0.0)

    @property
    def transports(self) -> List[TransportEvent]:
        """The transport events in this mission."""
        return [e for e in self.events if isinstance(e, TransportEvent)]

    @property
    def elements(self) -> List[SimElement]:
        """The elements created in this mission."""
        elements = {}
        for event in self.events:
            if isinstance(event, CreateEvent):
                for element in event.elements:
                    elements[element.id] = element
        return sorted(elements.values(), key=lambda e: e.sort_key)

    @property
    def is_crewed(self) -> bool:
        """True, if a crew member is created in this mission."""
        return any(isinstance(e, SimCrewMember) for e in self.elements)

    def count_crew(self) -> int:
        """
        Counts the crew members created in this mission, either directly or
        inside created carriers, in the current simulation state.

        Returns:
            int: The number of crew members.
        """
        crew = {}
        for element in self.elements:
            if isinstance(element, SimCrewMember):
                crew[element.id] = element
            elif isinstance(element, SimCarrier):
                for member in element.contents:
                    if isinstance(member, SimCrewMember):
                        crew[member.id] = member
        return len(crew)

    @property
    def crew_size(self) -> int:
        """The number of crew members created in this mission."""
        # NOTE: counted once in the initial state so the result does not
        # depend on where crew members are located during the simulation
        if self._crew_size is None:
            self._crew_size = self.count_crew()
        return self._crew_size

    @property
    def number_eva(self) -> int:
        """The number of extra-vehicular activities in this mission."""
        number_eva = 0
        for event in self.events:
            if isinstance(event, EvaEvent):
                number_eva += 1
            elif isinstance(event, ExplorationProcess):
                number_eva += event.number_eva
        return number_eva

    @property
    def eva_crew_time(self) -> float:
        """The crew time (hours) spent on extra-vehicular activities in this mission."""
        time = 0.0
        for event in self.events:
            if isinstance(event, EvaEvent):
                time += event.eva_duration * len(event.state_map)
            elif isinstance(event, ExplorationProcess):
                time += event.number_eva * event.eva_duration * len(event.state_map)
        return time

    @property
    def duration(self) -> float:
        """
        The duration (days) of this mission. The mission ends at the start of
        the next mission or, for the last mission, when its last event ends.
        """
        missions = sorted(
            self.state.missions, key=lambda m: (m.start_time, m.name, m.index)
        )
        position = next(i for i, m in enumerate(missions) if m is self)
        if position == len(missions) - 1:
            end_time = 0.0
            for event in self.events:
                event_end_time = self._mission_time(event)
                if isinstance(event, (TransportEvent, ExplorationProcess)):
                    event_end_time += event.duration
                end_time = max(end_time, event_end_time)
        else:
            end_time = missions[position + 1].start_time - self.start_time
        return self.settings.round_time(end_time)

    @property
    def destination_duration(self) -> float:
        """The duration (days) spent at the mission destination."""
        arrival = -1.0
        departure = -1.0
        for event in self.transports:
            if (
                event.destination is not None
                and event.destination == self.destination
                and arrival == -1
            ):
                arrival = self._mission_time(event) + event.duration
            elif event.origin is not None and event.origin == self.destination:
                departure = self._mission_time(event)
        if arrival < 0:
            return 0.0
        if departure < 0:
            return self.settings.round_time(self.duration - arrival)
        return self.settings.round_time(departure - arrival)

    @property
    def transit_duration(self) -> float:
        """The duration (days) until the first arrival at the mission destination."""
        for event in self.transports:
            if event.destination is not None and event.destination == self.destination:
                return self.settings.round_time(
                    self._mission_time(event) + event.duration
                )
        return self.settings.round_time(self.duration)

    @property
    def return_transit_duration(self) -> float:
        """The duration (days) of the transit from return origin to return destination."""
        transit_start = -1.0
        transit_end = -1.0
        for event in self.transports:
            if (
                event.destination is not None
                and event.destination == self.return_destination
            ):
                transit_end = self._mission_time(event) + event.duration
            if event.origin is not None and event.origin == self.return_origin:
                transit_start = self._mission_time(event)
        if transit_end != -1 and transit_start != -1:
            return self.settings.round_time(transit_end - transit_start)
        return 0.0

    @property
    def dormant_duration(self) -> float:
        """The duration (days) of this mission not in transit or at the destination."""
        return self.settings.round_time(
            self.duration
            - self.transit_duration
            - self.destination_duration
            - self.return_transit_duration
        )

    def _get_carriers_to(self, node: Optional[SimNode]) -> List[SimCarrier]:
        for event in self.transports:
            if node is not None and event.destination == node:
                return [e for e in event.elements if isinstance(e, SimCarrier)]
        return []

    @property
    def delivery_carriers(self) -> List[SimCarrier]:
        """The carriers in the first transport arriving at the mission destination."""
        return self._get_carriers_to(self.destination)

    @property
    def return_carriers(self) -> List[SimCarrier]:
        """The carriers in the first transport arriving at the return destination."""
        return self._get_carriers_to(self.return_destination)

    def _get_raw_capacity_to(self, node: Optional[SimNode]) -> float:
        capacity = 0.0
        if node is None:
            return capacity
        for event in self.events:
            if isinstance(event, FlightTransportEvent) and event.destination == node:
                capacity += event.edge.max_cargo_mass
            elif isinstance(event, SpaceTransportEvent) and event.destination == node:
                capacity += sum(
                    e.max_cargo_mass
                    for e in event.elements
                    if isinstance(e, SimCarrier)
                )
        return capacity

    @property
    def raw_delivery_capacity(self) -> float:
        """The cargo mass capacity (kg) of transports to the mission destination."""
        return self._get_raw_capacity_to(self.destination)

    @property
    def raw_return_capacity(self) -> float:
        """The cargo mass capacity (kg) of transports to the return destination."""
        return self._get_raw_capacity_to(self.return_destination)

    def _get_remaining_capacity_to(self, node: Optional[SimNode]) -> float:
        # pylint: disable=import-outside-toplevel
        from .simulator import PreSimulator

        capacity = 0.0
        if node is None:
            return capacity
        pre_sim = PreSimulator(self.state.scenario)
        reset = True
        for event in self.events:
            if not (
                isinstance(event, (FlightTransportEvent, SpaceTransportEvent))
                and event.destination == node
            ):
                continue
            pre_sim.simulate(
                self._mission_time(event) + self.start_time,
                priority=event.priority,
                reset=reset,
            )
            reset = False
            registrar = pre_sim.state.network.registrar
            if isinstance(event, FlightTransportEvent):
                capacity += event.edge.max_cargo_mass
            # NOTE: carriers are measured in the pre-simulated state at the time
            # of the transport (the reference implementation reads the cargo of
            # space transport carriers from their initial state)
            for element in event.elements:
                carrier = registrar.get(element.id)
                if not isinstance(carrier, SimCarrier):
                    continue
                if isinstance(event, FlightTransportEvent):
                    capacity -= carrier.cargo_mass
                else:
                    capacity += carrier.max_cargo_mass - carrier.cargo_mass
        return capacity

    @property
    def remaining_delivery_capacity(self) -> float:
        """The unused cargo mass capacity (kg) of transports to the mission destination."""
        return self._get_remaining_capacity_to(self.destination)

    @property
    def remaining_return_capacity(self) -> float:
        """The unused cargo mass capacity (kg) of transports to the return destination."""
        return self._get_remaining_capacity_to(self.return_destination)

    def __str__(self):
        return f"{self.name} ({self.start_date:%m/%d/%y})"

    def __repr__(self):
        return f"SimMission({self.name!r})"
