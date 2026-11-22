"""
Network locations (nodes and edges) used during simulation.
"""

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..schemas import Body, ClassOfSupply, EdgeType, NodeType, PropulsionType
from .elements import ElementContainer, SimElement


class SimLocation(ElementContainer):
    """
    Base class for a network location which contains elements.
    """

    def __init__(
        self,
        *,
        name: str,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
        index: int = 0,
    ):
        self._init_contents()
        self.id = id if id is not None else uuid4()
        self.name = name
        self.description = description
        self.index = index

    def can_add(self, element: SimElement) -> bool:  # pylint: disable=unused-argument
        """
        Checks if an element can be added (locations have unlimited capacity).

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element can be added.
        """
        return True

    def can_add_mass(self, added_mass: float) -> bool:
        # pylint: disable=unused-argument
        """
        Checks if a mass can be added (locations have unlimited capacity).

        Args:
            added_mass (float): The added mass (kg).

        Returns:
            bool: True, if the mass can be added.
        """
        return True

    def add(self, element: SimElement) -> bool:
        """
        Adds an element to this location, removing it from its prior container.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element was added.
        """
        self._attach(element)
        return True

    def remove(self, element: SimElement) -> bool:
        """
        Removes an element from this location.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element was removed.
        """
        return self._detach(element)

    @property
    def total_mass(self) -> float:
        """The total mass (kg) of contained elements, excluding crew members."""
        return self.cargo_mass

    @property
    def total_volume(self) -> float:
        """The total volume (m^3) of contained elements, excluding crew members."""
        return self.cargo_volume

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        """
        Gets the total mass, optionally restricted to a class of supply.

        Args:
            class_of_supply (:obj:`ClassOfSupply`): The class of supply to
                include (default: all).

        Returns:
            float: The total mass (kg).
        """
        if class_of_supply is None:
            return self.total_mass
        return sum(e.get_total_mass(class_of_supply) for e in self.contents)

    def __eq__(self, other):
        return isinstance(other, SimLocation) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class SimNode(SimLocation):
    """
    A network node.
    """

    def __init__(
        self,
        *,
        node_type: NodeType = NodeType.SURFACE,
        body: Body = Body.EARTH,
        illumination: Optional[float] = None,
        max_night_duration: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.node_type = NodeType(node_type)
        self.body = Body(body)
        #: Average fraction of time illuminated by the sun.
        self.illumination = 1.0 if illumination is None else illumination
        #: Duration (hours) of the longest continuous darkness.
        self.max_night_duration = max_night_duration or 0.0

    @property
    def is_surface(self) -> bool:
        """True, if this node is on the surface of a body."""
        return self.node_type == NodeType.SURFACE

    @property
    def is_orbital(self) -> bool:
        """True, if this node is in orbit around a body."""
        return self.node_type == NodeType.ORBITAL

    @property
    def is_exploration_site(self) -> bool:
        """
        True, if this node is an exploration destination, i.e., on a surface
        other than Earth or in orbit around the Sun.
        """
        return (self.is_surface and self.body != Body.EARTH) or (
            self.is_orbital and self.body == Body.SUN
        )


class SimBurn:
    """
    An impulsive burn required to traverse a space edge.
    """

    def __init__(
        self,
        *,
        time: float = 0.0,
        delta_v: float = 0.0,
        propulsion_type: PropulsionType = PropulsionType.OMS,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
    ):
        self.id = id if id is not None else uuid4()
        #: Type of the propulsion systems which perform the burn.
        self.propulsion_type = PropulsionType(propulsion_type)
        #: Time (days) relative to the start of the transport.
        self.time = time
        #: Change in velocity (m/s) to be achieved.
        self.delta_v = delta_v

    def __str__(self):
        return f"Burn ({self.delta_v} m/s)"


class SimEdge(SimLocation):
    """
    A network edge connecting two nodes.
    """

    def __init__(
        self,
        *,
        edge_type: EdgeType,
        origin: SimNode,
        destination: SimNode,
        duration: float = 0.0,
        burns: Optional[List[SimBurn]] = None,
        distance: float = 0.0,
        max_crew_size: int = 0,
        max_cargo_mass: float = 0.0,
        cost_per_transport: Optional[float] = None,
        min_departure_interval: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        #: Cost (millions of US dollars) of each transport along the edge.
        self.cost_per_transport = cost_per_transport
        #: Shortest time (days) between transports departing along the edge.
        self.min_departure_interval = min_departure_interval
        self.edge_type = EdgeType(edge_type)
        self.origin = origin
        self.destination = destination
        #: Duration (days) of a space or flight edge.
        self.duration = duration
        #: Burns required to traverse a space edge.
        self.burns: List[SimBurn] = list(burns) if burns is not None else []
        #: Distance (m) of a surface edge.
        self.distance = distance
        #: Crew capacity of a flight edge.
        self.max_crew_size = max_crew_size
        #: Cargo mass capacity (kg) of a flight edge.
        self.max_cargo_mass = max_cargo_mass

    @property
    def is_surface(self) -> bool:
        """True, if this is a surface edge."""
        return self.edge_type == EdgeType.SURFACE

    @property
    def is_space(self) -> bool:
        """True, if this is a space edge."""
        return self.edge_type == EdgeType.SPACE

    @property
    def is_flight(self) -> bool:
        """True, if this is a flight edge."""
        return self.edge_type == EdgeType.FLIGHT

    @property
    def is_exploration_site(self) -> bool:
        """True, if this is a surface edge on a body other than Earth."""
        return self.is_surface and self.origin.body != Body.EARTH


class SimNetwork:
    """
    A network of nodes and edges including a registrar of simulated elements.
    """

    def __init__(self):
        self.nodes: List[SimNode] = []
        self.edges: List[SimEdge] = []
        #: Elements which currently exist in the simulation by unique identifier.
        self.registrar: Dict[UUID, SimElement] = {}
        #: Elements which have been removed from the simulation by unique identifier.
        self.removed_registrar: Dict[UUID, SimElement] = {}

    @property
    def locations(self) -> List[SimLocation]:
        """All nodes followed by all edges."""
        return [*self.nodes, *self.edges]

    @property
    def elements(self) -> List[SimElement]:
        """The elements which currently exist in the simulation."""
        return sorted(self.registrar.values(), key=lambda e: (e.index, str(e.id)))

    def add(self, location: SimLocation) -> bool:
        """
        Adds a node or an edge to this network. Edges can only be added if
        their origin and destination nodes are in this network.

        Args:
            location (:obj:`SimLocation`): The node or edge.

        Returns:
            bool: True, if the location was added.
        """
        if isinstance(location, SimNode):
            if location not in self.nodes:
                self.nodes.append(location)
            return True
        if location.origin in self.nodes and location.destination in self.nodes:
            if location not in self.edges:
                self.edges.append(location)
            return True
        return False

    def get_location(self, location_id: UUID) -> Optional[SimLocation]:
        """
        Gets the location matching a unique identifier.

        Args:
            location_id (:obj:`uuid.UUID`): The unique identifier.

        Returns:
            :obj:`SimLocation`: The matching location if it exists, otherwise `None`.
        """
        for location in self.locations:
            if location.id == location_id:
                return location
        return None

    def get_contents_of(self, container: ElementContainer) -> List[SimElement]:
        """
        Gets the registered elements directly inside a container.

        Args:
            container (:obj:`ElementContainer`): The location or carrier.

        Returns:
            :obj:`List[SimElement]`: The elements.
        """
        return [e for e in self.elements if e.container is container]

    def get_complete_contents_of(self, location: SimLocation) -> List[SimElement]:
        """
        Gets the registered elements (recursively) at a location.

        Args:
            location (:obj:`SimLocation`): The location.

        Returns:
            :obj:`List[SimElement]`: The elements.
        """
        return [e for e in self.elements if e.location is location]

    def register(self, element: SimElement):
        """
        Registers an element and its (recursively) nested contents as existing.

        Args:
            element (:obj:`SimElement`): The element.
        """
        if isinstance(element, ElementContainer):
            for child in element.contents:
                self.register(child)
        self.removed_registrar.pop(element.id, None)
        self.registrar[element.id] = element

    def unregister(self, element: SimElement):
        """
        Registers an element and its (recursively) nested contents as removed.

        Args:
            element (:obj:`SimElement`): The element.
        """
        if isinstance(element, ElementContainer):
            for child in element.contents:
                self.unregister(child)
        self.registrar.pop(element.id, None)
        self.removed_registrar[element.id] = element
