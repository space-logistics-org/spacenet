"""
Manifest of demands packed in containers and containers loaded in carriers.

The manifest is built on the supply network (supply edges and supply points)
and the aggregated demands of an executed demand simulator. Because the supply
network is derived from the scenario, a stored manifest is reconciled with it
each time: packed demands and loads which no longer match are dropped.
"""

# pylint: disable=too-many-lines,too-many-public-methods

import re
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from ..schemas import Body, ClassOfSupply, Environment
from ..schemas.scenarios.manifest import (
    Manifest,
    ManifestContainer,
    ManifestContainerType,
    ManifestLoad,
    PackedDemand,
    ResourceRef,
    SupplyEdgeRef,
    SupplyPointRef,
)
from .records import ElementSnapshot
from .resources import Demand, SimResource
from .settings import Settings
from .simulator import DemandSimulator
from .supply import SupplyEdge, SupplyPoint

_LABELS = {
    ManifestContainerType.CTB: "CTB",
    ManifestContainerType.HALF_CTB: "Half CTB",
    ManifestContainerType.DOUBLE_CTB: "Double CTB",
    ManifestContainerType.LIQUID_TANK: "Liquid Tank",
    ManifestContainerType.LIQUID_TANK_DERIVATIVE: "Liquid Tank Derivative",
    ManifestContainerType.GAS_TANK: "Gas Tank",
    ManifestContainerType.GAS_TANK_DERIVATIVE: "Gas Tank Derivative",
    ManifestContainerType.SHOSS: "Shoss",
    ManifestContainerType.PRESSURIZED_SHOSS: "Press. Shoss",
    ManifestContainerType.CUSTOM: "Container",
}

_GAS_TANKS = (
    ManifestContainerType.GAS_TANK,
    ManifestContainerType.GAS_TANK_DERIVATIVE,
)
_LIQUID_TANKS = (
    ManifestContainerType.LIQUID_TANK,
    ManifestContainerType.LIQUID_TANK_DERIVATIVE,
)
_CARGO_BAGS = (ManifestContainerType.CTB,)


def container_factory(
    settings: Settings,
    container_type: ManifestContainerType,
    name: Optional[str] = None,
) -> ManifestContainer:
    """
    Creates an empty logistics container of a standard type.

    Args:
        settings (:obj:`Settings`): The simulation settings which size
            cargo transfer bags and tanks.
        container_type (:obj:`ManifestContainerType`): The container type.
        name (str): The container name (default: the type label).

    Returns:
        :obj:`ManifestContainer`: The container.
    """
    container_type = ManifestContainerType(container_type)
    pressurized = Environment.UNPRESSURIZED
    if container_type == ManifestContainerType.CTB:
        mass = settings.cargo_transfer_bag_mass
        volume = settings.cargo_transfer_bag_volume
        max_mass = settings.cargo_transfer_bag_max_mass
        max_volume = settings.cargo_transfer_bag_max_volume
    elif container_type == ManifestContainerType.HALF_CTB:
        mass, volume = 0.5532, 0.0265
        max_mass = settings.cargo_transfer_bag_max_mass / 2
        max_volume = settings.cargo_transfer_bag_max_volume / 2
    elif container_type == ManifestContainerType.DOUBLE_CTB:
        mass, volume = 1.383, 0.106
        max_mass = settings.cargo_transfer_bag_max_mass * 2
        max_volume = settings.cargo_transfer_bag_max_volume * 2
    elif container_type == ManifestContainerType.LIQUID_TANK:
        mass = settings.large_liquid_tank_mass
        volume = settings.large_liquid_tank_volume
        max_mass = settings.large_liquid_tank_max_mass
        max_volume = settings.large_liquid_tank_max_volume
    elif container_type == ManifestContainerType.LIQUID_TANK_DERIVATIVE:
        mass = settings.small_liquid_tank_mass
        volume = settings.small_liquid_tank_volume
        max_mass = settings.small_liquid_tank_max_mass
        max_volume = settings.small_liquid_tank_max_volume
    elif container_type == ManifestContainerType.GAS_TANK:
        mass = settings.large_gas_tank_mass
        volume = settings.large_gas_tank_volume
        max_mass = settings.large_gas_tank_max_mass
        max_volume = settings.large_gas_tank_max_volume
    elif container_type == ManifestContainerType.GAS_TANK_DERIVATIVE:
        mass = settings.small_gas_tank_mass
        volume = settings.small_gas_tank_volume
        max_mass = settings.small_gas_tank_max_mass
        max_volume = settings.small_gas_tank_max_volume
    elif container_type == ManifestContainerType.SHOSS:
        mass, volume, max_mass, max_volume = 120.0, 0.4444, 200.0, 0.4444
    elif container_type == ManifestContainerType.PRESSURIZED_SHOSS:
        mass, volume, max_mass, max_volume = 0.0, 0.8, 200.0, 0.8
        pressurized = Environment.PRESSURIZED
    else:
        mass, volume, max_mass, max_volume = 0.0, 0.0, 0.0, 0.0
    return ManifestContainer(
        name=name or _LABELS[container_type],
        container_type=container_type,
        mass=mass,
        volume=volume,
        max_cargo_mass=max_mass,
        max_cargo_volume=max_volume,
        environment=Environment.UNPRESSURIZED,
        cargo_environment=pressurized,
    )


def _format_time(time: float) -> str:
    return f"{time:.3f}"


def edge_key(edge_id: UUID, start_time: float, is_reversed: bool) -> str:
    """
    Gets the key which identifies a supply edge.

    Args:
        edge_id (:obj:`UUID`): The network edge unique identifier.
        start_time (float): The departure time (days).
        is_reversed (bool): True, if the edge is traversed in reverse.

    Returns:
        str: The key.
    """
    return f"e|{edge_id}|{_format_time(start_time)}|{int(bool(is_reversed))}"


def point_key(node_id: UUID, time: float) -> str:
    """
    Gets the key which identifies a supply point.

    Args:
        node_id (:obj:`UUID`): The node unique identifier.
        time (float): The arrival time (days).

    Returns:
        str: The key.
    """
    return f"p|{node_id}|{_format_time(time)}"


def _resource_key(
    resource_id: Optional[UUID], class_of_supply: int, environment: Environment
) -> str:
    environment = Environment(environment).value
    if resource_id is None:
        return f"g{int(class_of_supply)}|{environment}"
    return f"{resource_id}|{environment}"


class ManifestDemand:
    """
    A demand aggregated to a supply point (node demand) or to a supply edge
    (edge demand) which can be packed in containers.
    """

    def __init__(
        self, point: SupplyPoint, edge: Optional[SupplyEdge], demand: Demand, key: str
    ):
        #: Supply point at which the demand is supplied.
        self.point = point
        #: Supply edge during which the demand occurs (`None` for a node demand).
        self.edge = edge
        self.demand = demand
        #: Key which identifies this demand.
        self.key = key

    @property
    def resource(self) -> SimResource:
        """The demanded resource."""
        return self.demand.resource

    @property
    def amount(self) -> float:
        """The demanded amount (units)."""
        return self.demand.amount

    @property
    def is_edge_demand(self) -> bool:
        """True, if the demand occurs during a transport."""
        return self.edge is not None

    def __str__(self):
        return f"{self.demand} at {self.point}"

    def __repr__(self):
        return f"ManifestDemand({self})"


class ManifestItem:
    """
    An amount of an aggregated demand packed in a container.
    """

    def __init__(self, demand: ManifestDemand, amount: float):
        self.demand = demand
        self.amount = amount

    @property
    def mass(self) -> float:
        """The packed mass (kg)."""
        return Demand(self.demand.resource, self.amount).mass

    @property
    def volume(self) -> float:
        """The packed volume (m^3)."""
        return Demand(self.demand.resource, self.amount).volume


class SimManifestContainer:
    """
    A logistics container and the demands packed in it.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, container: ManifestContainer):
        self.id = container.id
        self.name = container.name
        self.container_type = ManifestContainerType(container.container_type)
        self.mass = container.mass
        self.volume = container.volume
        self.max_cargo_mass = container.max_cargo_mass
        self.max_cargo_volume = container.max_cargo_volume
        self.environment = Environment(container.environment)
        self.cargo_environment = Environment(container.cargo_environment)
        self.items: List[ManifestItem] = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"SimManifestContainer({self.name!r})"


class SimManifest:
    """
    Packs aggregated demands in containers and loads containers in the
    carriers of supply edges.

    Args:
        simulator (:obj:`DemandSimulator`): An executed demand simulator.
        manifest (:obj:`Manifest`): A stored manifest to reconcile with the
            supply network of the simulator.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, simulator: DemandSimulator, manifest: Optional[Manifest] = None):
        self.settings: Settings = simulator.settings
        #: Supply edges in order of decreasing arrival time.
        self.edges: List[SupplyEdge] = list(simulator.supply_edges)
        #: Supply points in order of decreasing time.
        self.points: List[SupplyPoint] = list(simulator.supply_points)
        #: Aggregated demands (edge demands before node demands for each point).
        self.demands: List[ManifestDemand] = []
        #: Containers in order of creation.
        self.containers: List[SimManifestContainer] = []
        #: Descriptions of stored entries which no longer match the scenario.
        self.dropped: List[str] = []
        self._edges_by_key: Dict[str, SupplyEdge] = {}
        self._points_by_key: Dict[str, SupplyPoint] = {}
        self._demands_by_key: Dict[str, ManifestDemand] = {}
        # containers loaded on each (supply edge, carrier)
        self._loads: Dict[Tuple[int, UUID], List[SimManifestContainer]] = {}
        self._import_demands(simulator)
        if manifest is not None:
            self._reconcile(manifest)

    @classmethod
    def create(cls, scenario, manifest: Optional[Manifest] = None) -> "SimManifest":
        """
        Creates a manifest for a scenario by simulating its demands.

        Args:
            scenario (:obj:`Scenario`): The scenario.
            manifest (:obj:`Manifest`): The stored manifest (default: the
                manifest of the scenario).

        Returns:
            :obj:`SimManifest`: The manifest.
        """
        simulator = DemandSimulator(
            scenario, packing_demands_added=False, items_repaired=True
        )
        simulator.simulate()
        return cls(simulator, scenario.manifest if manifest is None else manifest)

    # ------------------------------------------------------------------ keys

    def get_edge_key(self, edge: SupplyEdge) -> str:
        """Gets the key which identifies a supply edge."""
        return edge_key(edge.edge.id, edge.start_time, edge.is_reversed)

    def get_point_key(self, point: SupplyPoint) -> str:
        """Gets the key which identifies a supply point."""
        return point_key(point.node.id, point.time)

    def get_edge(self, key: str) -> Optional[SupplyEdge]:
        """Gets the supply edge matching a key."""
        return self._edges_by_key.get(key)

    def get_point(self, key: str) -> Optional[SupplyPoint]:
        """Gets the supply point matching a key."""
        return self._points_by_key.get(key)

    def get_demand_by_key(self, key: str) -> Optional[ManifestDemand]:
        """Gets the aggregated demand matching a key."""
        return self._demands_by_key.get(key)

    def get_container(self, container_id: UUID) -> Optional[SimManifestContainer]:
        """Gets the container matching a unique identifier."""
        for container in self.containers:
            if container.id == container_id:
                return container
        return None

    def get_carrier(
        self, edge: SupplyEdge, carrier_id: UUID
    ) -> Optional[ElementSnapshot]:
        """Gets the snapshot of a carrier transported on a supply edge."""
        for carrier in edge.all_carriers:
            if carrier.id == carrier_id:
                return carrier
        return None

    def _canonical_point(self, point: SupplyPoint) -> SupplyPoint:
        # NOTE: coincident arrivals at a node share one supply point
        return self._points_by_key.get(self.get_point_key(point), point)

    # ---------------------------------------------------------------- import

    def _import_demands(self, simulator: DemandSimulator):
        for point in self.points:
            self._points_by_key[self.get_point_key(point)] = point
        for edge in self.edges:
            self._edges_by_key[self.get_edge_key(edge)] = edge
            for carrier in edge.all_carriers:
                self._loads[(id(edge), carrier.id)] = []
        edge_demands = dict(
            (id(edge), demands) for edge, demands in simulator.aggregated_edge_demands
        )
        node_demands = dict(
            (id(point), demands) for point, demands in simulator.aggregated_node_demands
        )
        for point in self.points:
            for edge in self.edges:
                if self._canonical_point(edge.point) is not point:
                    continue
                for demand in edge_demands.get(id(edge), []):
                    self._add_demand(point, edge, demand)
            for demand in node_demands.get(id(point), []):
                self._add_demand(point, None, demand)

    def _add_demand(
        self, point: SupplyPoint, edge: Optional[SupplyEdge], demand: Demand
    ):
        if demand.amount <= 0:
            return  # produced resources are not packed
        resource = demand.resource
        prefix = self.get_point_key(point) if edge is None else self.get_edge_key(edge)
        key = f"d|{prefix}|" + _resource_key(
            resource.id, resource.class_of_supply, resource.environment
        )
        manifest_demand = ManifestDemand(point, edge, demand.copy(), key)
        self.demands.append(manifest_demand)
        self._demands_by_key[key] = manifest_demand

    def _reconcile(self, manifest: Manifest):
        """Restores a stored manifest, dropping entries which no longer match."""
        for stored in manifest.containers:
            container = SimManifestContainer(stored)
            self.containers.append(container)
            for packed in stored.contents:
                ref = packed.resource
                if packed.edge_demand is not None:
                    prefix = edge_key(
                        packed.edge_demand.edge,
                        packed.edge_demand.start_time,
                        packed.edge_demand.reversed,
                    )
                else:
                    prefix = point_key(packed.point.node, packed.point.time)
                key = f"d|{prefix}|" + _resource_key(
                    ref.resource, ref.class_of_supply, ref.environment
                )
                demand = self._demands_by_key.get(key)
                if demand is None:
                    self.dropped.append(
                        f"{container.name}: packed demand no longer exists "
                        f"({packed.amount:g} units, class of supply "
                        f"{int(ref.class_of_supply)})"
                    )
                    continue
                amount = min(packed.amount, self.get_remaining_amount(demand))
                if amount < packed.amount:
                    self.dropped.append(
                        f"{container.name}: packed amount of {demand.resource} "
                        f"reduced from {packed.amount:g} to {amount:g}"
                    )
                if amount > 0:
                    container.items.append(ManifestItem(demand, amount))
        for load in manifest.loads:
            ref = load.supply_edge
            edge = self._edges_by_key.get(
                edge_key(ref.edge, ref.start_time, ref.reversed)
            )
            if edge is None or (id(edge), load.carrier) not in self._loads:
                self.dropped.append(
                    f"Transport or carrier no longer exists for {len(load.containers)} "
                    "loaded container(s)"
                )
                continue
            for container_id in load.containers:
                container = self.get_container(container_id)
                if container is None:
                    self.dropped.append("Loaded container no longer exists")
                elif container not in self._loads[(id(edge), load.carrier)]:
                    self._loads[(id(edge), load.carrier)].append(container)

    def to_schema(self) -> Manifest:
        """
        Converts this manifest to its object schema.

        Returns:
            :obj:`Manifest`: The manifest.
        """
        containers = []
        for container in self.containers:
            contents = []
            for item in container.items:
                demand = item.demand
                resource = demand.resource
                contents.append(
                    PackedDemand(
                        resource=ResourceRef(
                            resource=resource.id,
                            class_of_supply=resource.class_of_supply,
                            environment=resource.environment,
                        ),
                        amount=item.amount,
                        point=SupplyPointRef(
                            node=demand.point.node.id, time=demand.point.time
                        ),
                        edge_demand=(
                            None if demand.edge is None else self._edge_ref(demand.edge)
                        ),
                    )
                )
            containers.append(
                ManifestContainer(
                    id=container.id,
                    name=container.name,
                    container_type=container.container_type,
                    mass=container.mass,
                    volume=container.volume,
                    max_cargo_mass=container.max_cargo_mass,
                    max_cargo_volume=container.max_cargo_volume,
                    environment=container.environment,
                    cargo_environment=container.cargo_environment,
                    contents=contents,
                )
            )
        loads = []
        for edge in self.edges:
            for carrier in edge.all_carriers:
                loaded = self._loads[(id(edge), carrier.id)]
                if loaded:
                    loads.append(
                        ManifestLoad(
                            supply_edge=self._edge_ref(edge),
                            carrier=carrier.id,
                            containers=[c.id for c in loaded],
                        )
                    )
        return Manifest(containers=containers, loads=loads)

    @staticmethod
    def _edge_ref(edge: SupplyEdge) -> SupplyEdgeRef:
        return SupplyEdgeRef(
            edge=edge.edge.id,
            start_time=edge.start_time,
            end_time=edge.end_time,
            reversed=edge.is_reversed,
        )

    # --------------------------------------------------------------- amounts

    def get_demands_as_packed(self, demand: ManifestDemand) -> List[ManifestItem]:
        """Gets the packed amounts of an aggregated demand."""
        return [
            item
            for container in self.containers
            for item in container.items
            if item.demand is demand
        ]

    def get_packed_amount(self, demand: ManifestDemand) -> float:
        """Gets the packed amount (units) of an aggregated demand."""
        return self.settings.round_demand(
            sum(item.amount for item in self.get_demands_as_packed(demand))
        )

    def get_remaining_amount(self, demand: ManifestDemand) -> float:
        """Gets the amount (units) of an aggregated demand which remains to be packed."""
        return self.settings.round_demand(
            demand.amount - self.get_packed_amount(demand)
        )

    def get_packed_items(
        self, container: SimManifestContainer, point: Optional[SupplyPoint] = None
    ) -> List[ManifestItem]:
        """
        Gets the demands packed in a container, optionally restricted to
        those which are still in the container at a supply point (i.e.,
        which are supplied at the same or a later time).
        """
        if point is None:
            return list(container.items)
        return [i for i in container.items if i.demand.point.time >= point.time]

    def get_container_cargo_mass(
        self, container: SimManifestContainer, point: Optional[SupplyPoint] = None
    ) -> float:
        """Gets the cargo mass (kg) of a container at a supply point."""
        return sum(i.mass for i in self.get_packed_items(container, point))

    def get_container_cargo_volume(
        self, container: SimManifestContainer, point: Optional[SupplyPoint] = None
    ) -> float:
        """Gets the cargo volume (m^3) of a container at a supply point."""
        return sum(i.volume for i in self.get_packed_items(container, point))

    def get_loaded_containers(
        self, edge: SupplyEdge, carrier_id: UUID
    ) -> List[SimManifestContainer]:
        """Gets the containers loaded in a carrier on a supply edge."""
        return list(self._loads.get((id(edge), carrier_id), []))

    def get_carrier_containers(
        self, carrier_id: UUID, point: SupplyPoint
    ) -> List[SimManifestContainer]:
        """
        Gets the containers loaded in a carrier on any supply edge which
        arrives no later than a supply point.
        """
        containers = []
        for edge in self.edges:
            if edge.end_time > point.time:
                continue
            for container in self._loads.get((id(edge), carrier_id), []):
                if container not in containers:
                    containers.append(container)
        return containers

    def get_carrier_cargo_mass(
        self, carrier: ElementSnapshot, point: SupplyPoint
    ) -> float:
        """Gets the cargo mass (kg) of a carrier at a supply point."""
        mass = carrier.cargo_mass
        for container in self.get_carrier_containers(carrier.id, point):
            mass += container.mass + self.get_container_cargo_mass(container, point)
        return mass

    def get_carrier_cargo_volume(
        self, carrier: ElementSnapshot, point: SupplyPoint
    ) -> float:
        """Gets the cargo volume (m^3) of a carrier at a supply point."""
        volume = carrier.cargo_volume
        for container in self.get_carrier_containers(carrier.id, point):
            volume += container.volume
        return volume

    # ----------------------------------------------------------- supply chain

    def get_next_supply_point(self, edge: SupplyEdge) -> Optional[SupplyPoint]:
        """
        Gets the supply point (earlier in time) which services the origin of
        a supply edge. Transports from the surface of Earth are not serviced.
        """
        if edge.origin.is_surface and edge.origin.body == Body.EARTH:
            return None
        point = None
        for candidate in self.points:
            if (
                candidate.node == edge.origin
                and candidate.time <= edge.start_time
                and (point is None or candidate.time > point.time)
            ):
                point = candidate
        return point

    def get_supply_edges(self, point: SupplyPoint) -> List[SupplyEdge]:
        """Gets the supply edges which can supply a supply point."""
        return [
            e
            for e in self.edges
            if e.destination == point.node and e.end_time <= point.time
        ]

    def _loaded_edges(self, container: SimManifestContainer) -> List[SupplyEdge]:
        return [
            edge
            for edge in self.edges
            if any(
                container in self._loads[(id(edge), carrier.id)]
                for carrier in edge.all_carriers
            )
        ]

    def get_initial_supply_point(
        self, container: SimManifestContainer
    ) -> Optional[SupplyPoint]:
        """
        Gets the supply point to which a container is initially assigned: the
        arrival of the last transport it is loaded on or else the earliest
        supply point of its packed demands.
        """
        edge = None
        for candidate in self._loaded_edges(container):
            if edge is None or candidate.end_time > edge.end_time:
                edge = candidate
        point = None if edge is None else self._canonical_point(edge.point)
        for item in container.items:
            candidate = item.demand.point
            if edge is None or candidate.time >= edge.end_time:
                if point is None or candidate.time < point.time:
                    point = candidate
        return point

    def get_current_supply_point(
        self, container: SimManifestContainer
    ) -> Optional[SupplyPoint]:
        """
        Gets the supply point to which a container is currently assigned in
        the manifesting process, i.e., the earliest supply point reached by
        following the transports it is loaded on backwards in time.
        """
        point = self.get_initial_supply_point(container)
        if point is None:
            return None
        for edge in self.edges:
            if edge.end_time <= point.time and edge in self._loaded_edges(container):
                candidate = self.get_next_supply_point(edge)
                if candidate is not None and candidate.time < point.time:
                    point = candidate
        return point

    def get_empty_containers(self) -> List[SimManifestContainer]:
        """Gets the containers without packed demands which are not loaded."""
        return [
            c
            for c in self.containers
            if not c.items and self.get_initial_supply_point(c) is None
        ]

    def is_edge_demand_container(self, container: SimManifestContainer) -> bool:
        """
        Checks if a container holds a demand which occurs during a transport
        on which the container is not yet loaded.
        """
        return self._get_edge_demand_edge(container) is not None

    def _get_edge_demand_edge(
        self, container: SimManifestContainer
    ) -> Optional[SupplyEdge]:
        for item in container.items:
            edge = item.demand.edge
            if edge is not None and edge not in self._loaded_edges(container):
                return edge
        return None

    def is_manifested(
        self, container: Optional[SimManifestContainer], point: Optional[SupplyPoint]
    ) -> bool:
        """
        Checks if a container is loaded on a transport which arrives at the
        node of a supply point no later than the supply point.
        """
        if container is None or point is None:
            return False
        for edge in self._loaded_edges(container):
            if edge.destination == point.node and edge.end_time <= point.time:
                return True
        return False

    # --------------------------------------------------------------- packing

    def _get_packable_amount(
        self,
        demand: ManifestDemand,
        container: SimManifestContainer,
        point: Optional[SupplyPoint],
    ) -> float:
        """Gets the amount of a demand which fits in a container at a supply point."""
        resource = demand.resource
        # resource containers only accept resources which require the
        # stowage environment they provide
        if (
            self.settings.environment_constrained
            and resource.environment != container.cargo_environment
        ):
            return 0.0
        amount = self.get_remaining_amount(demand)
        if resource.unit_mass != 0:
            amount = min(
                amount,
                self.settings.round_demand(
                    (
                        container.max_cargo_mass
                        - self.get_container_cargo_mass(container, point)
                    )
                    / resource.unit_mass
                ),
            )
        if self.settings.volume_constrained and resource.unit_volume != 0:
            amount = min(
                amount,
                self.settings.round_demand(
                    (
                        container.max_cargo_volume
                        - self.get_container_cargo_volume(container, point)
                    )
                    / resource.unit_volume
                ),
            )
        return max(0.0, amount)

    def can_pack_demand(
        self,
        demand: Optional[ManifestDemand],
        container: Optional[SimManifestContainer],
    ) -> bool:
        """
        Checks if (part of) an aggregated demand can be packed in a container.

        Args:
            demand (:obj:`ManifestDemand`): The aggregated demand.
            container (:obj:`SimManifestContainer`): The container.

        Returns:
            bool: True, if the demand can be packed.
        """
        if demand is None or container is None:
            return False
        container_point = self.get_current_supply_point(container)
        # NOTE: the reference implementation requires the entire demand to
        # fit in the (empty) container; here any amount which fits can be packed
        if self._get_packable_amount(demand, container, container_point) <= 0:
            return False
        if container_point is None:
            return True
        if self.is_manifested(container, container_point):
            return False
        if demand.is_edge_demand:
            return demand.point is container_point
        return (
            demand.point.node == container_point.node
            and demand.point.time <= container_point.time
        )

    def pack_demand(
        self, demand: ManifestDemand, container: SimManifestContainer
    ) -> float:
        """
        Packs as much of an aggregated demand in a container as fits.

        Args:
            demand (:obj:`ManifestDemand`): The aggregated demand.
            container (:obj:`SimManifestContainer`): The container.

        Returns:
            float: The packed amount (units).
        """
        container_point = self.get_current_supply_point(container)
        if container_point is not None and not (
            demand.point.node == container_point.node
            and demand.point.time <= container_point.time
        ):
            return 0.0
        amount = self._get_packable_amount(demand, container, container_point)
        if amount <= 0:
            return 0.0
        for item in container.items:
            if item.demand is demand:
                item.amount += amount
                return amount
        container.items.append(ManifestItem(demand, amount))
        return amount

    def can_unpack_demand(
        self,
        demand: Optional[ManifestDemand],
        container: Optional[SimManifestContainer] = None,
    ) -> bool:
        """
        Checks if an aggregated demand can be unpacked (from one container
        or from all containers).
        """
        if demand is None:
            return False
        if container is None:
            return self.get_packed_amount(demand) != 0
        return any(item.demand is demand for item in container.items)

    def unpack_demand(
        self, demand: ManifestDemand, container: Optional[SimManifestContainer] = None
    ):
        """
        Unpacks an aggregated demand from one container or from all containers.

        Args:
            demand (:obj:`ManifestDemand`): The aggregated demand.
            container (:obj:`SimManifestContainer`): The container (default: all).
        """
        for other in self.containers if container is None else [container]:
            other.items = [i for i in other.items if i.demand is not demand]

    def can_auto_pack_demand(self, demand: Optional[ManifestDemand]) -> bool:
        """Checks if an aggregated demand has an amount which remains to be packed."""
        return demand is not None and self.get_remaining_amount(demand) != 0

    def _get_name(self, label: str) -> str:
        """Gets the next unused container name for a label."""
        pattern = re.compile(re.escape(label) + r" (\d+)$")
        number = 0
        for container in self.containers:
            match = pattern.match(container.name)
            if match:
                number = max(number, int(match.group(1)))
        return f"{label} {number + 1}"

    def add_container(
        self, container_type: ManifestContainerType, name: Optional[str] = None
    ) -> SimManifestContainer:
        """
        Adds an empty container of a standard type to this manifest.

        Args:
            container_type (:obj:`ManifestContainerType`): The container type.
            name (str): The container name (default: numbered type label).

        Returns:
            :obj:`SimManifestContainer`: The container.
        """
        container_type = ManifestContainerType(container_type)
        container = SimManifestContainer(
            container_factory(
                self.settings,
                container_type,
                name or self._get_name(_LABELS[container_type]),
            )
        )
        self.containers.append(container)
        return container

    def remove_container(self, container: SimManifestContainer):
        """
        Removes a container (and its packed demands) from this manifest.

        Args:
            container (:obj:`SimManifestContainer`): The container.
        """
        self.containers = [c for c in self.containers if c is not container]
        for loaded in self._loads.values():
            loaded[:] = [c for c in loaded if c is not container]

    def _pack_in_new_containers(
        self,
        demand: ManifestDemand,
        small_type: ManifestContainerType,
        large_type: ManifestContainerType,
        small_max_mass: float,
        small_max_volume: float,
    ):
        resource = demand.resource
        while self.get_remaining_amount(demand) > 0:
            remaining = self.get_remaining_amount(demand)
            if remaining * resource.unit_mass > small_max_mass or (
                self.settings.volume_constrained
                and remaining * resource.unit_volume > small_max_volume
            ):
                container = self.add_container(large_type)
            else:
                container = self.add_container(small_type)
            container.environment = resource.environment
            container.cargo_environment = resource.environment
            # NOTE: guards against containers without capacity for the
            # resource which the reference implementation creates indefinitely
            if self.pack_demand(demand, container) <= 0:
                self.remove_container(container)
                break

    def _pack_in_existing_containers(self, demand: ManifestDemand, container_types):
        for container in list(self.containers):
            if container.container_type in container_types and self.can_pack_demand(
                demand, container
            ):
                self.pack_demand(demand, container)

    def auto_pack_demand(self, demand: ManifestDemand):
        """
        Packs the remaining amount of an aggregated demand in containers
        chosen by class of supply:

         * propellants and fuels (COS 1): new liquid tanks
         * gases (COS 203): existing and new gas tanks
         * water (COS 201): existing and new liquid tanks
         * crew provisions, crew operations, maintenance, and waste (COS 2,
           3, 4, 7): existing and new cargo transfer bags
         * stowage and restraint (COS 5): ignored (only an estimate)
         * exploration, infrastructure, transportation, and miscellaneous
           (COS 6, 8, 9, 10): one custom container sized to the demand

        Args:
            demand (:obj:`ManifestDemand`): The aggregated demand.
        """
        # pylint: disable=too-many-branches
        if self.get_remaining_amount(demand) <= 0:
            return
        settings = self.settings
        resource = demand.resource
        cos = resource.class_of_supply

        def is_a(*classes) -> bool:
            return any(cos.is_instance_of(c) for c in classes)

        if is_a(ClassOfSupply.COS_1):
            self._pack_in_new_containers(
                demand,
                ManifestContainerType.LIQUID_TANK_DERIVATIVE,
                ManifestContainerType.LIQUID_TANK,
                settings.small_liquid_tank_max_mass,
                settings.small_liquid_tank_max_volume,
            )
        elif cos == ClassOfSupply.COS_203:
            self._pack_in_existing_containers(demand, _GAS_TANKS)
            self._pack_in_new_containers(
                demand,
                ManifestContainerType.GAS_TANK_DERIVATIVE,
                ManifestContainerType.GAS_TANK,
                settings.small_gas_tank_max_mass,
                settings.small_gas_tank_max_volume,
            )
        elif cos == ClassOfSupply.COS_201:
            self._pack_in_existing_containers(demand, _LIQUID_TANKS)
            self._pack_in_new_containers(
                demand,
                ManifestContainerType.LIQUID_TANK_DERIVATIVE,
                ManifestContainerType.LIQUID_TANK,
                settings.small_liquid_tank_max_mass,
                settings.small_liquid_tank_max_volume,
            )
        elif is_a(
            ClassOfSupply.COS_2,
            ClassOfSupply.COS_3,
            ClassOfSupply.COS_4,
            ClassOfSupply.COS_7,
        ):
            self._pack_in_existing_containers(demand, _CARGO_BAGS)
            self._pack_in_new_containers(
                demand,
                ManifestContainerType.CTB,
                ManifestContainerType.CTB,
                settings.cargo_transfer_bag_max_mass,
                settings.cargo_transfer_bag_max_volume,
            )
        elif is_a(ClassOfSupply.COS_5):
            pass  # only an estimate of stowage and restraint
        elif is_a(
            ClassOfSupply.COS_6,
            ClassOfSupply.COS_8,
            ClassOfSupply.COS_9,
            ClassOfSupply.COS_10,
        ):
            if is_a(ClassOfSupply.COS_6):
                label = "Science"
            elif is_a(ClassOfSupply.COS_8):
                label = "Infrastructure"
            elif is_a(ClassOfSupply.COS_9):
                label = "Transportation"
            else:
                label = "Miscellaneous"
            remaining = Demand(resource, self.get_remaining_amount(demand))
            container = SimManifestContainer(
                ManifestContainer(
                    id=uuid4(),
                    name=self._get_name(label),
                    container_type=ManifestContainerType.CUSTOM,
                    mass=max(0.0, remaining.mass * resource.packing_factor),
                    volume=max(0.0, remaining.volume),
                    max_cargo_mass=max(0.0, remaining.mass),
                    max_cargo_volume=max(0.0, remaining.volume),
                    environment=resource.environment,
                    cargo_environment=resource.environment,
                )
            )
            self.containers.append(container)
            if self.pack_demand(demand, container) <= 0:
                self.remove_container(container)

    # ----------------------------------------------------------- manifesting

    def can_manifest_container(
        self,
        container: Optional[SimManifestContainer],
        edge: Optional[SupplyEdge],
        carrier: Optional[ElementSnapshot],
    ) -> bool:
        """
        Checks if a container can be loaded in a carrier on a supply edge.

        Args:
            container (:obj:`SimManifestContainer`): The container.
            edge (:obj:`SupplyEdge`): The supply edge.
            carrier (:obj:`ElementSnapshot`): The carrier.

        Returns:
            bool: True, if the container can be loaded.
        """
        if container is None or edge is None or carrier is None:
            return False
        if (id(edge), carrier.id) not in self._loads:
            return False
        point = self.get_current_supply_point(container)
        if point is None:
            return False
        demand_edge = self._get_edge_demand_edge(container)
        if demand_edge is not None:
            # demands during a transport must travel on that transport
            if edge is not demand_edge:
                return False
        elif not (edge.destination == point.node and edge.end_time <= point.time):
            return False
        settings = self.settings
        if (
            self.get_carrier_cargo_mass(carrier, point)
            + container.mass
            + self.get_container_cargo_mass(container, point)
            - carrier.max_cargo_mass
            >= settings.mass_precision / 2
        ):
            return False
        if settings.volume_constrained and (
            self.get_carrier_cargo_volume(carrier, point)
            + container.volume
            - carrier.max_cargo_volume
            >= settings.volume_precision / 2
        ):
            return False
        if (
            settings.environment_constrained
            and container.environment == Environment.PRESSURIZED
            and carrier.cargo_environment == Environment.UNPRESSURIZED.value
        ):
            return False
        # NOTE: the reference implementation does not check the cargo mass
        # capacity of a flight which then fails during simulation
        if edge.edge.is_flight and (
            container.mass
            + self.get_container_cargo_mass(container, point)
            - self.get_net_cargo_mass(edge)
            >= settings.mass_precision / 2
        ):
            return False
        return not self.is_manifested(container, point)

    def get_net_cargo_mass(self, edge: SupplyEdge) -> float:
        """
        Gets the unused cargo mass capacity (kg) of a supply edge including
        the containers loaded on it.

        Args:
            edge (:obj:`SupplyEdge`): The supply edge.

        Returns:
            float: The unused cargo mass capacity (kg).
        """
        point = self._canonical_point(edge.point)
        containers = []
        for carrier in edge.all_carriers:
            for container in self.get_carrier_containers(carrier.id, point):
                if container not in containers:
                    containers.append(container)
        return edge.net_cargo_mass - sum(
            c.mass + self.get_container_cargo_mass(c, point) for c in containers
        )

    def manifest_container(
        self,
        container: SimManifestContainer,
        edge: SupplyEdge,
        carrier: ElementSnapshot,
    ) -> bool:
        """
        Loads a container in a carrier on a supply edge.

        Args:
            container (:obj:`SimManifestContainer`): The container.
            edge (:obj:`SupplyEdge`): The supply edge.
            carrier (:obj:`ElementSnapshot`): The carrier.

        Returns:
            bool: True, if the container was loaded.
        """
        if not self.can_manifest_container(container, edge, carrier):
            return False
        self._loads[(id(edge), carrier.id)].append(container)
        return True

    def can_unmanifest_container(
        self, container: Optional[SimManifestContainer], edge: Optional[SupplyEdge]
    ) -> bool:
        """Checks if a container is loaded on a supply edge."""
        if container is None or edge is None:
            return False
        return edge in self._loaded_edges(container)

    def unmanifest_container(self, container: SimManifestContainer, edge: SupplyEdge):
        """
        Unloads a container from a supply edge and from all earlier supply edges.

        Args:
            container (:obj:`SimManifestContainer`): The container.
            edge (:obj:`SupplyEdge`): The supply edge.
        """
        if not self.can_unmanifest_container(container, edge):
            return
        for other in self.edges:
            if other is edge or other.end_time < edge.end_time:
                for carrier in other.all_carriers:
                    loaded = self._loads[(id(other), carrier.id)]
                    loaded[:] = [c for c in loaded if c is not container]

    def reset(self):
        """Removes all containers (and their packed demands and loads)."""
        self.containers = []
        for loaded in self._loads.values():
            loaded.clear()

    def auto_manifest(self):
        """
        Packs all aggregated demands and loads the containers in carriers,
        working backwards in time from the last supply point. Each container
        is loaded in the first carrier (of the last-arriving transport) with
        sufficient capacity.
        """
        for point in self.points:
            for demand in self.demands:
                if demand.point is point and demand.is_edge_demand:
                    self.auto_pack_demand(demand)
            for demand in self.demands:
                if demand.point is point and not demand.is_edge_demand:
                    self.auto_pack_demand(demand)
            for edge_demands in (True, False):
                for container in list(self.containers):
                    if (
                        self.get_current_supply_point(container) is not point
                        or self.is_edge_demand_container(container) != edge_demands
                    ):
                        continue
                    self._manifest_in_first_carrier(container)

    def _manifest_in_first_carrier(self, container: SimManifestContainer) -> bool:
        for edge in self.edges:
            for carrier in edge.carriers:
                if self.manifest_container(container, edge, carrier):
                    return True
        return False
