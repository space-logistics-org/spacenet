import pytest
from app.database.api.models import element, edge, node, resource
from spacenet.schemas.element import ElementKind
from spacenet.schemas.edge import EdgeType
from spacenet.schemas.node import NodeType
from spacenet.schemas.resource import ResourceType
from spacenet.test.utilities import (
    lunar_sortie_elements,
    lunar_sortie_edges,
    lunar_sortie_nodes,
    lunar_sortie_resources,
    KIND_TO_SCHEMA,
)
from .utilities import db

pytestmark = [pytest.mark.unit, pytest.mark.database, pytest.mark.lunar_sortie]


KIND_TO_CTOR = {
    ElementKind.Element: element.Element,
    ElementKind.ElementCarrier: element.ElementCarrier,
    ElementKind.ResourceContainer: element.ResourceContainer,
    ElementKind.HumanAgent: element.HumanAgent,
    ElementKind.RoboticAgent: element.RoboticAgent,
    ElementKind.Propulsive: element.PropulsiveVehicle,
    ElementKind.Surface: element.SurfaceVehicle,
    EdgeType.Surface: edge.SurfaceEdge,
    EdgeType.Flight: edge.FlightEdge,
    EdgeType.Space: edge.SpaceEdge,
    NodeType.Surface: node.SurfaceNode,
    NodeType.Orbital: node.OrbitalNode,
    NodeType.Lagrange: node.LagrangeNode,
    ResourceType.discrete: resource.DiscreteResource,
    ResourceType.continuous: resource.ContinuousResource,
}


@pytest.mark.parametrize(
    "domain_objects",
    (
        pytest.param(
            pytest.lazy_fixture("lunar_sortie_" + obj_type + "s"),
            marks=getattr(pytest.mark, obj_type),
        )
        for obj_type in ["element", "edge", "node", "resource"]
    ),
)
def test_database_with_lunar_sortie_data(domain_objects, db):
    for obj in domain_objects:
        obj_type = obj["type"]
        schema_cls = KIND_TO_SCHEMA[obj_type]
        domain_object = schema_cls.parse_obj(obj)
        model_ctor = KIND_TO_CTOR[obj_type]
        db_domain_obj = model_ctor(**domain_object.dict())
        db.add(db_domain_obj)
        db.commit()
        for attr, value in obj.items():
            assert value == getattr(db_domain_obj, attr)
        assert isinstance(db_domain_obj.id, int)
        db.delete(db_domain_obj)
        db.commit()
