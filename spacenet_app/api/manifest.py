"""
Endpoints to view and change the manifest of a scenario.

Each endpoint reconciles the stored manifest with the demands and transports
of the scenario, applies one operation, and returns the updated manifest
(to be stored in the scenario by the client) with a view of it.
"""

from fastapi import APIRouter

from spacenet.simulation import ManifestResult, SimManifest

from .models import (
    AddContainersRequest,
    ContainersRequest,
    DemandKeysRequest,
    ManifestRequest,
)

router = APIRouter()


def _get_demands(manifest: SimManifest, keys):
    demands = [manifest.get_demand_by_key(key) for key in keys]
    if any(d is None for d in demands):
        raise ValueError("Unknown aggregated demand.")
    return demands


def _get_containers(manifest: SimManifest, container_ids):
    containers = [manifest.get_container(i) for i in container_ids]
    if any(c is None for c in containers):
        raise ValueError("Unknown container.")
    return containers


def _get_edge(manifest: SimManifest, key):
    edge = manifest.get_edge(key)
    if edge is None:
        raise ValueError("Unknown transport.")
    return edge


@router.post("/view")
def view_manifest(request: ManifestRequest) -> ManifestResult:
    """
    Views the manifest of a scenario.
    """
    manifest = SimManifest.create(request.scenario)
    return ManifestResult.create(manifest, request.selection)


@router.post("/containers")
def add_containers(request: AddContainersRequest) -> ManifestResult:
    """
    Adds empty containers of a standard type.
    """
    manifest = SimManifest.create(request.scenario)
    for _ in range(request.count):
        manifest.add_container(request.container_type)
    return ManifestResult.create(manifest, request.selection)


@router.post("/containers/remove")
def remove_containers(request: ContainersRequest) -> ManifestResult:
    """
    Removes containers (and their packed demands).
    """
    manifest = SimManifest.create(request.scenario)
    for container in _get_containers(manifest, request.container_ids):
        manifest.remove_container(container)
    return ManifestResult.create(manifest, request.selection)


@router.post("/pack")
def pack_demands(request: DemandKeysRequest) -> ManifestResult:
    """
    Packs as much of aggregated demands in a container as fits.
    """
    manifest = SimManifest.create(request.scenario)
    (container,) = _get_containers(manifest, [request.container_id])
    for demand in _get_demands(manifest, request.demand_keys):
        if manifest.can_pack_demand(demand, container):
            manifest.pack_demand(demand, container)
    return ManifestResult.create(manifest, request.selection)


@router.post("/unpack")
def unpack_demands(request: DemandKeysRequest) -> ManifestResult:
    """
    Unpacks aggregated demands from one container or from all containers.
    """
    manifest = SimManifest.create(request.scenario)
    container = None
    if request.container_id is not None:
        (container,) = _get_containers(manifest, [request.container_id])
    for demand in _get_demands(manifest, request.demand_keys):
        manifest.unpack_demand(demand, container)
    return ManifestResult.create(manifest, request.selection)


@router.post("/auto-pack")
def auto_pack_demands(request: DemandKeysRequest) -> ManifestResult:
    """
    Packs aggregated demands in containers chosen by class of supply.
    """
    manifest = SimManifest.create(request.scenario)
    for demand in _get_demands(manifest, request.demand_keys):
        manifest.auto_pack_demand(demand)
    return ManifestResult.create(manifest, request.selection)


@router.post("/load")
def load_containers(request: ContainersRequest) -> ManifestResult:
    """
    Loads containers in a carrier on a supply edge (where feasible).
    """
    manifest = SimManifest.create(request.scenario)
    edge = _get_edge(manifest, request.edge_key)
    carrier = manifest.get_carrier(edge, request.carrier_id)
    if carrier is None:
        raise ValueError("Unknown carrier.")
    for container in _get_containers(manifest, request.container_ids):
        manifest.manifest_container(container, edge, carrier)
    return ManifestResult.create(manifest, request.selection)


@router.post("/unload")
def unload_containers(request: ContainersRequest) -> ManifestResult:
    """
    Unloads containers from a supply edge (and from all earlier supply
    edges) or, if no supply edge is given, from all supply edges.
    """
    manifest = SimManifest.create(request.scenario)
    edges = (
        manifest.edges
        if request.edge_key is None
        else [_get_edge(manifest, request.edge_key)]
    )
    for container in _get_containers(manifest, request.container_ids):
        for edge in edges:
            manifest.unmanifest_container(container, edge)
    return ManifestResult.create(manifest, request.selection)


@router.post("/auto")
def auto_manifest(request: ManifestRequest) -> ManifestResult:
    """
    Packs all aggregated demands and loads the containers in carriers.
    """
    manifest = SimManifest.create(request.scenario)
    manifest.auto_manifest()
    return ManifestResult.create(manifest, request.selection)


@router.post("/reset")
def reset_manifest(request: ManifestRequest) -> ManifestResult:
    """
    Removes all containers (and their packed demands and loads).
    """
    manifest = SimManifest.create(request.scenario)
    manifest.reset()
    manifest.dropped = []
    return ManifestResult.create(manifest, request.selection)
