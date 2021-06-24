import json

import pkg_resources
import pytest
from app.database.api.models import element, edge, node, resource
from spacenet.schemas.element import *
from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge, EdgeType
from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode, NodeType
from spacenet.schemas.resource import DiscreteResource, ContinuousResource, ResourceType
from .utilities import db

from spacenet import schemas

pytestmark = [pytest.mark.unit, pytest.mark.database]


KIND_TO_CTORS = {
    ElementKind.Element: (Element, element.Element),
    ElementKind.ElementCarrier: (ElementCarrier, element.ElementCarrier),
    ElementKind.ResourceContainer: (ResourceContainer, element.ResourceContainer),
    ElementKind.HumanAgent: (HumanAgent, element.HumanAgent),
    ElementKind.RoboticAgent: (RoboticAgent, element.RoboticAgent),
    ElementKind.Propulsive: (PropulsiveVehicle, element.PropulsiveVehicle),
    ElementKind.Surface: (SurfaceVehicle, element.SurfaceVehicle),
    EdgeType.Surface: (SurfaceEdge, edge.SurfaceEdge),
    EdgeType.Flight: (FlightEdge, edge.FlightEdge),
    EdgeType.Space: (SpaceEdge, edge.SpaceEdge),
    NodeType.Surface: (SurfaceNode, node.SurfaceNode),
    NodeType.Orbital: (OrbitalNode, node.OrbitalNode),
    NodeType.Lagrange: (LagrangeNode, node.LagrangeNode),
    ResourceType.discrete: (DiscreteResource, resource.DiscreteResource),
    ResourceType.continuous: (ContinuousResource, resource.ContinuousResource),
}


@pytest.fixture(params=["altair", "ares_1", "ares_5", "orion", "sortie_elements"])
def elements(request):
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, f"lunar_sortie/{request.param}.json"
        )
    )


@pytest.fixture()
def edges():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_edges.json"
        )
    )


@pytest.fixture()
def nodes():
    yield json.loads(
        pkg_resources.resource_string(
            schemas.__name__, "lunar_sortie/sortie_nodes.json"
        )
    )


@pytest.fixture()
def resources():
    yield json.loads(
        pkg_resources.resource_string(schemas.__name__, "lunar_sortie/fuels.json")
    )


@pytest.mark.parametrize(
    "domain_objects",
    map(
        lambda obj_type: pytest.param(
            pytest.lazy_fixture(obj_type + "s"), marks=getattr(pytest.mark, obj_type)
        ),
        ["element", "edge", "node", "resource"],
    ),
)
def test_lunar_sortie(domain_objects, db):
    for obj in domain_objects:
        schema_cls, model_ctor = KIND_TO_CTORS[obj["type"]]
        domain_object = schema_cls.parse_obj(obj)
        db_domain_obj = model_ctor(**domain_object.dict())
        db.add(db_domain_obj)
        db.commit()
        for attr, value in obj.items():
            assert value == getattr(db_domain_obj, attr)
        assert isinstance(db_domain_obj.id, int)
        db.delete(db_domain_obj)
        db.commit()
