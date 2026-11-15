"""
Object schemas to view a manifest.
"""

from typing import List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ...schemas import Manifest
from ..manifest import SimManifest, SimManifestContainer
from ..records import ElementSnapshot
from ..supply import SupplyEdge


class ManifestDemandView(CamelModel):
    """
    An aggregated demand and its packed amount.
    """

    key: str = Field(..., description="Key which identifies the demand")
    point_key: str = Field(..., description="Key of the supply point")
    point_label: str = Field(..., description="Label of the supply point")
    edge_key: Optional[str] = Field(
        None, description="Key of the supply edge (demands during a transport)"
    )
    resource_name: str = Field(..., description="Resource name")
    class_of_supply: int = Field(..., description="Class of supply")
    environment: str = Field(..., description="Required stowage environment")
    units: str = Field(..., description="Unit resource label")
    amount: float = Field(..., description="Demanded amount (units)")
    mass: float = Field(..., description="Demanded mass (kg)")
    packed_amount: float = Field(0.0, description="Packed amount (units)")
    remaining_amount: float = Field(0.0, description="Amount to pack (units)")
    can_unpack: bool = Field(False, description="True, if the demand can be unpacked")
    can_auto_pack: bool = Field(
        False, description="True, if the demand can be automatically packed"
    )
    can_pack: bool = Field(
        False, description="True, if the demand can be packed in the selected container"
    )


class PackedDemandView(CamelModel):
    """
    An amount of an aggregated demand packed in a container.
    """

    demand_key: str = Field(..., description="Key of the aggregated demand")
    point_label: str = Field(..., description="Label of the supply point")
    resource_name: str = Field(..., description="Resource name")
    units: str = Field(..., description="Unit resource label")
    amount: float = Field(..., description="Packed amount (units)")
    mass: float = Field(..., description="Packed mass (kg)")
    volume: float = Field(..., description="Packed volume (m^3)")


class ManifestContainerView(CamelModel):
    """
    A logistics container, its packed demands, and the transports it is loaded on.
    """

    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    container_type: str = Field(..., description="Container type")
    environment: str = Field(..., description="Required stowage environment")
    cargo_environment: str = Field(..., description="Stowage environment provided")
    mass: float = Field(0.0, description="Empty mass (kg)")
    volume: float = Field(0.0, description="Volume (m^3)")
    max_cargo_mass: float = Field(0.0, description="Cargo mass capacity (kg)")
    max_cargo_volume: float = Field(0.0, description="Cargo volume capacity (m^3)")
    cargo_mass: float = Field(0.0, description="Packed mass (kg)")
    cargo_volume: float = Field(0.0, description="Packed volume (m^3)")
    total_mass: float = Field(0.0, description="Total mass (kg)")
    point_key: Optional[str] = Field(
        None, description="Key of the supply point the container is assigned to"
    )
    point_label: Optional[str] = Field(
        None, description="Label of the supply point the container is assigned to"
    )
    edge_keys: List[str] = Field(
        [], description="Keys of the supply edges the container is loaded on"
    )
    edge_labels: List[str] = Field(
        [], description="Labels of the supply edges the container is loaded on"
    )
    contents: List[PackedDemandView] = Field([], description="Packed demands")
    can_manifest: bool = Field(
        False,
        description="True, if the container can be loaded in the selected carrier",
    )


class ManifestCarrierView(CamelModel):
    """
    A carrier transported on a supply edge and the containers loaded in it.
    """

    id: UUID = Field(..., description="Element unique identifier")
    name: str = Field(..., description="Name")
    depth: int = Field(0, description="Nesting depth (0 for a top-level carrier)")
    cargo_environment: Optional[str] = Field(
        None, description="Stowage environment provided"
    )
    max_cargo_mass: float = Field(0.0, description="Cargo mass capacity (kg)")
    max_cargo_volume: float = Field(0.0, description="Cargo volume capacity (m^3)")
    cargo_mass: float = Field(
        0.0, description="Cargo mass (kg) including loaded containers"
    )
    cargo_volume: float = Field(
        0.0, description="Cargo volume (m^3) including loaded containers"
    )
    containers: List[UUID] = Field(
        [], description="Unique identifiers of the containers loaded on this edge"
    )


class ManifestEdgeView(CamelModel):
    """
    A transport along an edge and its carriers.
    """

    key: str = Field(..., description="Key which identifies the supply edge")
    label: str = Field(..., description="Label")
    edge: UUID = Field(..., description="Network edge unique identifier")
    origin: str = Field(..., description="Name of the node of departure")
    destination: str = Field(..., description="Name of the node of arrival")
    start_time: float = Field(..., description="Departure time (days)")
    end_time: float = Field(..., description="Arrival time (days)")
    is_flight: bool = Field(False, description="True, for a flight transport")
    max_cargo_mass: float = Field(0.0, description="Cargo mass capacity (kg)")
    net_cargo_mass: float = Field(
        0.0, description="Unused cargo mass capacity (kg) including loaded containers"
    )
    carriers: List[ManifestCarrierView] = Field(
        [], description="Carriers (nested carriers follow their parent)"
    )


class ManifestSelection(CamelModel):
    """
    Selection for which a manifest view reports the feasible actions.
    """

    container_id: Optional[UUID] = Field(
        None, description="Container in which demands would be packed"
    )
    edge_key: Optional[str] = Field(
        None, description="Supply edge on which containers would be loaded"
    )
    carrier_id: Optional[UUID] = Field(
        None, description="Carrier in which containers would be loaded"
    )


class ManifestAnalysis(CamelModel):
    """
    View of a manifest: aggregated demands, containers, and transports.
    """

    demands: List[ManifestDemandView] = Field([], description="Aggregated demands")
    containers: List[ManifestContainerView] = Field([], description="Containers")
    edges: List[ManifestEdgeView] = Field(
        [], description="Transports in order of departure"
    )
    total_mass: float = Field(0.0, description="Demanded mass (kg)")
    packed_mass: float = Field(0.0, description="Packed mass (kg)")
    loaded_container_count: int = Field(
        0, description="Number of containers loaded on a transport"
    )

    @classmethod
    def create(
        cls, manifest: SimManifest, selection: Optional[ManifestSelection] = None
    ) -> "ManifestAnalysis":
        """
        Creates a view of a manifest.

        Args:
            manifest (:obj:`SimManifest`): The manifest.
            selection (:obj:`ManifestSelection`): The selection for which
                to report the feasible actions.

        Returns:
            :obj:`ManifestAnalysis`: The view.
        """
        # pylint: disable=too-many-locals
        selection = selection or ManifestSelection()
        selected_container = (
            None
            if selection.container_id is None
            else manifest.get_container(selection.container_id)
        )
        selected_edge = (
            None
            if selection.edge_key is None
            else manifest.get_edge(selection.edge_key)
        )
        selected_carrier = (
            None
            if selected_edge is None or selection.carrier_id is None
            else manifest.get_carrier(selected_edge, selection.carrier_id)
        )

        demands = []
        packed_mass = 0.0
        for demand in manifest.demands:
            resource = demand.resource
            packed = manifest.get_packed_amount(demand)
            packed_mass += packed * resource.unit_mass
            demands.append(
                ManifestDemandView(
                    key=demand.key,
                    point_key=manifest.get_point_key(demand.point),
                    point_label=str(demand.point),
                    edge_key=(
                        None
                        if demand.edge is None
                        else manifest.get_edge_key(demand.edge)
                    ),
                    resource_name=resource.name,
                    class_of_supply=int(resource.class_of_supply),
                    environment=resource.environment.value,
                    units=resource.units,
                    amount=demand.amount,
                    mass=demand.demand.mass,
                    packed_amount=packed,
                    remaining_amount=manifest.get_remaining_amount(demand),
                    can_unpack=manifest.can_unpack_demand(demand),
                    can_auto_pack=manifest.can_auto_pack_demand(demand),
                    can_pack=manifest.can_pack_demand(demand, selected_container),
                )
            )

        containers = []
        loaded_count = 0
        for container in manifest.containers:
            view = cls._view_container(manifest, container)
            view.can_manifest = manifest.can_manifest_container(
                container, selected_edge, selected_carrier
            )
            loaded_count += 1 if view.edge_keys else 0
            containers.append(view)

        return cls(
            demands=demands,
            containers=containers,
            edges=[
                cls._view_edge(manifest, edge)
                for edge in sorted(manifest.edges, key=lambda e: e.start_time)
            ],
            total_mass=sum(d.mass for d in demands),
            packed_mass=packed_mass,
            loaded_container_count=loaded_count,
        )

    @staticmethod
    def _view_container(
        manifest: SimManifest, container: SimManifestContainer
    ) -> ManifestContainerView:
        # pylint: disable=protected-access
        point = manifest.get_current_supply_point(container)
        edges = manifest._loaded_edges(container)
        cargo_mass = manifest.get_container_cargo_mass(container)
        return ManifestContainerView(
            id=container.id,
            name=container.name,
            container_type=container.container_type.value,
            environment=container.environment.value,
            cargo_environment=container.cargo_environment.value,
            mass=container.mass,
            volume=container.volume,
            max_cargo_mass=container.max_cargo_mass,
            max_cargo_volume=container.max_cargo_volume,
            cargo_mass=cargo_mass,
            cargo_volume=manifest.get_container_cargo_volume(container),
            total_mass=container.mass + cargo_mass,
            point_key=None if point is None else manifest.get_point_key(point),
            point_label=None if point is None else str(point),
            edge_keys=[manifest.get_edge_key(e) for e in edges],
            edge_labels=[str(e) for e in edges],
            contents=[
                PackedDemandView(
                    demand_key=item.demand.key,
                    point_label=str(item.demand.point),
                    resource_name=item.demand.resource.name,
                    units=item.demand.resource.units,
                    amount=item.amount,
                    mass=item.mass,
                    volume=item.volume,
                )
                for item in container.items
            ],
        )

    @staticmethod
    def _view_edge(manifest: SimManifest, edge: SupplyEdge) -> ManifestEdgeView:
        # pylint: disable=protected-access
        point = manifest._canonical_point(edge.point)
        carriers: List[ManifestCarrierView] = []

        def add(carrier: ElementSnapshot, depth: int):
            if carrier.is_carrier:
                carriers.append(
                    ManifestCarrierView(
                        id=carrier.id,
                        name=carrier.name,
                        depth=depth,
                        cargo_environment=carrier.cargo_environment,
                        max_cargo_mass=carrier.max_cargo_mass,
                        max_cargo_volume=carrier.max_cargo_volume,
                        cargo_mass=manifest.get_carrier_cargo_mass(carrier, point),
                        cargo_volume=manifest.get_carrier_cargo_volume(carrier, point),
                        containers=[
                            c.id
                            for c in manifest.get_loaded_containers(edge, carrier.id)
                        ],
                    )
                )
                depth += 1
            for child in carrier.contents:
                add(child, depth)

        for carrier in edge.carriers:
            add(carrier, 0)
        return ManifestEdgeView(
            key=manifest.get_edge_key(edge),
            label=str(edge),
            edge=edge.edge.id,
            origin=edge.origin.name,
            destination=edge.destination.name,
            start_time=edge.start_time,
            end_time=edge.end_time,
            is_flight=edge.edge.is_flight,
            max_cargo_mass=edge.max_cargo_mass,
            net_cargo_mass=manifest.get_net_cargo_mass(edge),
            carriers=carriers,
        )


class ManifestResult(CamelModel):
    """
    A manifest, its view, and the stored entries which were dropped because
    they no longer match the scenario.
    """

    manifest: Manifest = Field(..., description="Manifest")
    view: ManifestAnalysis = Field(..., description="View of the manifest")
    dropped: List[str] = Field(
        [], description="Descriptions of stored entries which were dropped"
    )

    @classmethod
    def create(
        cls, manifest: SimManifest, selection: Optional[ManifestSelection] = None
    ) -> "ManifestResult":
        """Creates the result of a manifest operation."""
        return cls(
            manifest=manifest.to_schema(),
            view=ManifestAnalysis.create(manifest, selection),
            dropped=list(manifest.dropped),
        )
