import json

import pkg_resources
import pytest
from app.database.api import models
from spacenet.schemas.element import *
from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge, EdgeType
from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode, NodeType
from spacenet.schemas.resource import DiscreteResource, ContinuousResource, ResourceType
from .utilities import db

from spacenet import schemas

pytestmark = [pytest.mark.unit, pytest.mark.database]


KIND_TO_SCHEMA = {
    ElementKind.Element: (Element, models.element.Element),
    ElementKind.ElementCarrier: (ElementCarrier, models.element.ElementCarrier),
    ElementKind.ResourceContainer: (
        ResourceContainer,
        models.element.ResourceContainer,
    ),
    ElementKind.HumanAgent: (HumanAgent, models.element.HumanAgent),
    ElementKind.RoboticAgent: (RoboticAgent, models.element.RoboticAgent),
    ElementKind.Propulsive: (PropulsiveVehicle, models.element.PropulsiveVehicle),
    ElementKind.Surface: (SurfaceVehicle, models.element.SurfaceVehicle),
    EdgeType.Surface: (SurfaceEdge, models.edge.SurfaceEdge),
    EdgeType.Flight: (FlightEdge, models.edge.FlightEdge),
    EdgeType.Space: (SpaceEdge, models.edge.SpaceEdge),
    NodeType.Surface: (SurfaceNode, models.node.SurfaceNode),
    NodeType.Orbital: (OrbitalNode, models.node.OrbitalNode),
    NodeType.Lagrange: (LagrangeNode, models.node.LagrangeNode),
    ResourceType.discrete: (DiscreteResource, models.resource.DiscreteResource),
    ResourceType.continuous: (ContinuousResource, models.resource.ContinuousResource),
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


@pytest.mark.element
def test_lunar_sortie_elements(elements, db):
    for element_obj in elements:
        schema_ctor, model_ctor = KIND_TO_SCHEMA[element_obj["type"]]
        element = schema_ctor.parse_obj(element_obj)
        db_element = model_ctor(**element.dict())
        db.add(db_element)
        db.commit()
        for attr, value in element_obj.items():
            assert value == getattr(db_element, attr)
        db.delete(db_element)
        db.commit()


@pytest.mark.edge
def test_lunar_sortie_edges(edges, db):
    for edge_obj in edges:
        schema_ctor, model_ctor = KIND_TO_SCHEMA[edge_obj["type"]]
        edge = schema_ctor.parse_obj(edge_obj)
        db_edge = model_ctor(**edge.dict())
        db.add(db_edge)
        db.commit()
        for attr, value in edge_obj.items():
            assert value == getattr(db_edge, attr)
        db.delete(db_edge)
        db.commit()


@pytest.mark.node
def test_lunar_sortie_nodes(nodes, db):
    for node_obj in nodes:
        schema_ctor, model_ctor = KIND_TO_SCHEMA[node_obj["type"]]
        node = schema_ctor.parse_obj(node_obj)
        db_node = model_ctor(**node.dict())
        db.add(db_node)
        db.commit()
        for attr, value in node_obj.items():
            assert value == getattr(db_node, attr)
        db.delete(db_node)
        db.commit()


@pytest.mark.resource
def test_lunar_sortie_resources(resources, db):
    for resource_obj in resources:
        schema_ctor, model_ctor = KIND_TO_SCHEMA[resource_obj["type"]]
        resource = schema_ctor.parse_obj(resource_obj)
        db_resource = model_ctor(**resource.dict())
        db.add(db_resource)
        db.commit()
        for attr, value in resource_obj.items():
            assert value == getattr(db_resource, attr)
        db.delete(db_resource)
        db.commit()
