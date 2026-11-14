"""
Records of simulation history including measures of effectiveness.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import UUID

if TYPE_CHECKING:  # pragma: no cover
    from .elements import ElementContainer, SimElement
    from .network import SimLocation, SimNetwork
    from .resources import SimResource

#: Crew time category for time not available for productive activities.
CREW_TIME_UNAVAILABLE = "Unavailable"
#: Crew time category for repairing failed parts.
CREW_TIME_CORRECTIVE_MAINTENANCE = "Corrective Maintenance"
#: Crew time category for scheduled maintenance.
CREW_TIME_PREVENTATIVE_MAINTENANCE = "Preventative Maintenance"
#: Crew time category for exploration.
CREW_TIME_EXPLORATION = "Exploration"


@dataclass
class SimScavenge:
    """
    A part scavenged from a decommissioned element to satisfy a demand.
    """

    time: float
    item: "SimResource"
    amount: float
    location: Optional["SimLocation"]
    element: "SimElement"


@dataclass
class SimRepair:
    """
    A part repaired (rather than replaced) to satisfy a demand.
    """

    time: float
    item: "SimResource"
    amount: float
    #: Crew time (hours) required for the repair.
    repair_time: float
    #: Mass (kg, generic COS 4) required for the repair.
    repair_mass: float
    location: Optional["SimLocation"]
    element: "SimElement"


@dataclass
class MoeCrewSurfaceDays:
    """
    Crew surface days: time (days) spent by one crew member at an exploration site.
    """

    time: float
    location: "SimLocation"
    amount: float


@dataclass
class MoeCrewTime:
    """
    Crew time (hours) spent on a category of activity.
    """

    time: float
    location: "SimLocation"
    type: str
    amount: float


@dataclass
class MoeExplorationCapability:
    """
    Exploration capability: mass (kg) of exploration and infrastructure items
    (COS 6 and COS 8) present with one crew member for a duration (days).
    """

    time: float
    location: "SimLocation"
    mass: float
    duration: float


@dataclass
class MoeExplorationMassDelivered:
    """
    Mass (kg) of exploration and infrastructure items (COS 6 and COS 8)
    delivered to an exploration site.
    """

    time: float
    location: "SimLocation"
    amount: float


@dataclass
class MoeLaunchMass:
    """
    Mass (kg) launched from the surface of Earth.
    """

    time: float
    location: "SimLocation"
    amount: float


@dataclass
class MoeMassCapacityUtilization:
    """
    Mass (kg) carried compared to the capacity (kg) of a transport.
    """

    time: float
    location: "SimLocation"
    amount: float
    capacity: float


@dataclass
class ElementSnapshot:
    """
    Snapshot of an element at a point in time.
    """

    id: UUID
    name: str
    type: Optional[str]
    state: Optional[str]
    mass: float
    total_mass: float
    volume: float = 0.0
    cargo_mass: float = 0.0
    max_cargo_mass: float = 0.0
    cargo_volume: float = 0.0
    max_cargo_volume: float = 0.0
    crew_size: int = 0
    #: True, if the element can carry other elements.
    is_carrier: bool = False
    #: Contained resource amounts (units) by resource name.
    resources: Dict[str, float] = field(default_factory=dict)
    #: Nested elements.
    contents: List["ElementSnapshot"] = field(default_factory=list)

    @classmethod
    def create(cls, element: "SimElement") -> "ElementSnapshot":
        """
        Records a snapshot of an element and its (nested) contents.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            :obj:`ElementSnapshot`: The snapshot.
        """
        # pylint: disable=import-outside-toplevel
        from .elements import SimCarrier, SimResourceContainer, SimResourceTank

        snapshot = cls(
            id=element.id,
            name=element.name,
            type=None if element.element_type is None else element.element_type.value,
            state=None if element.current_state is None else element.current_state.name,
            mass=element.mass,
            total_mass=element.total_mass,
            volume=element.volume,
        )
        if isinstance(element, (SimCarrier, SimResourceContainer, SimResourceTank)):
            snapshot.cargo_mass = element.cargo_mass
            snapshot.max_cargo_mass = element.max_cargo_mass
            snapshot.cargo_volume = element.cargo_volume
            snapshot.max_cargo_volume = element.max_cargo_volume
        if isinstance(element, (SimResourceContainer, SimResourceTank)):
            snapshot.resources = {r.name: a for r, a in element.contents.items()}
        if isinstance(element, SimCarrier):
            snapshot.is_carrier = True
            snapshot.crew_size = element.crew_size
            snapshot.contents = [cls.create(e) for e in element.contents]
            fuel_tank = getattr(element, "fuel_tank", None)
            if fuel_tank is not None and fuel_tank.resource is not None:
                snapshot.resources = {fuel_tank.resource.name: fuel_tank.amount}
        return snapshot

    @property
    def all_carriers(self) -> List["ElementSnapshot"]:
        """This carrier and all (recursively) nested carriers."""
        carriers = [self] if self.is_carrier else []
        for child in self.contents:
            carriers.extend(child.all_carriers)
        return carriers


@dataclass
class NetworkSnapshot:
    """
    Snapshot of the elements at each network location at a point in time.
    """

    time: float
    #: Top-level element snapshots by location unique identifier.
    locations: Dict[UUID, List[ElementSnapshot]] = field(default_factory=dict)
    #: Location names by location unique identifier.
    location_names: Dict[UUID, str] = field(default_factory=dict)

    @classmethod
    def create(cls, time: float, network: "SimNetwork") -> "NetworkSnapshot":
        """
        Records a snapshot of a network.

        Args:
            time (float): The simulation time (days).
            network (:obj:`SimNetwork`): The network.

        Returns:
            :obj:`NetworkSnapshot`: The snapshot.
        """
        snapshot = cls(time=time)
        for location in network.locations:
            snapshot.location_names[location.id] = location.name
            snapshot.locations[location.id] = [
                ElementSnapshot.create(e) for e in location.contents
            ]
        return snapshot

    def get_elements(self, location_id: UUID) -> List[ElementSnapshot]:
        """
        Gets the top-level elements at a location.

        Args:
            location_id (:obj:`UUID`): The location unique identifier.

        Returns:
            :obj:`List[ElementSnapshot]`: The element snapshots.
        """
        return self.locations.get(location_id, [])

    def get_total_mass(self, location_id: UUID) -> float:
        """
        Gets the total mass at a location.

        Args:
            location_id (:obj:`UUID`): The location unique identifier.

        Returns:
            float: The total mass (kg).
        """
        return sum(e.total_mass for e in self.get_elements(location_id))


class LocationSnapshot:
    """
    Snapshot of the container of each element at a point in time.
    """

    def __init__(self, time: float, network: "SimNetwork"):
        self.time = time
        self._containers: Dict["SimElement", "ElementContainer"] = {
            element: element.container for element in network.elements
        }

    @property
    def elements(self) -> List["SimElement"]:
        """The elements which existed at the time of this snapshot."""
        return list(self._containers)

    def get_container(self, element: "SimElement") -> Optional["ElementContainer"]:
        """
        Gets the container (location or carrier) of an element.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            :obj:`ElementContainer`: The container, or `None` if the element did not exist.
        """
        return self._containers.get(element)

    def get_location(self, element: "SimElement") -> Optional["SimLocation"]:
        """
        Gets the location (node or edge) of an element.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            :obj:`SimLocation`: The location, or `None` if the element did not exist.
        """
        # pylint: disable=import-outside-toplevel
        from .elements import SimElement

        container = self._containers.get(element)
        while isinstance(container, SimElement):
            container = self._containers.get(container)
        return container
