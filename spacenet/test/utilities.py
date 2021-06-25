import json
import pkg_resources
import pytest

from spacenet import schemas
from spacenet.schemas.element import *
from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge, EdgeType
from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode, NodeType
from spacenet.schemas.resource import DiscreteResource, ContinuousResource, ResourceType


@pytest.fixture(params=["altair", "ares_1", "ares_5", "orion", "sortie_elements"])
def lunar_sortie_elements(request):
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, f"lunar_sortie/{request.param}.json"
        )
    )


@pytest.fixture()
def lunar_sortie_edges():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_edges.json"
        )
    )


@pytest.fixture()
def lunar_sortie_nodes():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_nodes.json"
        )
    )


@pytest.fixture()
def lunar_sortie_resources():
    yield json.loads(
        pkg_resources.resource_string(schemas.__name__, "lunar_sortie/fuels.json")
    )


KIND_TO_SCHEMA = {
    ElementKind.Element: Element,
    ElementKind.ElementCarrier: ElementCarrier,
    ElementKind.ResourceContainer: ResourceContainer,
    ElementKind.HumanAgent: HumanAgent,
    ElementKind.RoboticAgent: RoboticAgent,
    ElementKind.Propulsive: PropulsiveVehicle,
    ElementKind.Surface: SurfaceVehicle,
    EdgeType.Surface: SurfaceEdge,
    EdgeType.Flight: FlightEdge,
    EdgeType.Space: SpaceEdge,
    NodeType.Surface: SurfaceNode,
    NodeType.Orbital: OrbitalNode,
    NodeType.Lagrange: LagrangeNode,
    ResourceType.discrete: DiscreteResource,
    ResourceType.continuous: ContinuousResource,
}