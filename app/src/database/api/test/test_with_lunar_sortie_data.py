"""
This module contains tests for API routes via the lunar sortie data.
"""
import pytest
from fastapi.testclient import TestClient

from ..database import get_db
from ..main import app
from ....auth_dependencies import current_user
from ..schemas.constants import CREATE_SCHEMAS
from .utilities import get_current_user, get_test_db
from spacenet.src.schemas.element import Element
from spacenet.src.schemas.node import Node
from spacenet.src.schemas.edge import Edge
from spacenet.src.schemas.resource import Resource
from .utilities import (
    lunar_sortie_elements,
    lunar_sortie_edges,
    lunar_sortie_nodes,
    lunar_sortie_resources,
)

pytestmark = [pytest.mark.unit, pytest.mark.database, pytest.mark.lunar_sortie]

app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[current_user] = get_current_user

client = TestClient(app)


def schema_superclass(type_):
    """
    :param type_: subclass of exactly one of Element, Node, Edge, or Resource schemas
    :return: the superclass of type_ from (Element, Node, Edge, Resource)
    """
    for super_ in (Element, Node, Edge, Resource):
        if issubclass(type_, super_):
            return super_


TYPE_TO_SUPER = {cls: schema_superclass(cls) for cls in CREATE_SCHEMAS}


SUPER_TO_PREFIX = {Element: "element", Edge: "edge", Node: "node", Resource: "resource"}


def object_to_prefix(obj: dict) -> str:
    """
    :param obj: object, which fits some schema in CREATE_SCHEMAS
    :return: routing prefix for the object schema's type
    """
    for schema in CREATE_SCHEMAS:
        try:
            obj = schema.parse_obj(obj)
        except ValueError:
            pass
        else:
            super_ = TYPE_TO_SUPER[schema]
            return SUPER_TO_PREFIX[super_]
    else:
        raise ValueError(f"Could not find prefix mapping to {obj}")


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
def test_routers_with_lunar_sortie_data(domain_objects):
    for obj in domain_objects:
        prefix = object_to_prefix(obj)
        post_response = client.post(f"/{prefix}/", json=obj)
        assert 201 == post_response.status_code
        result = post_response.json()
        id_ = result.get("id")
        with_id = dict(obj, id=id_)
        assert with_id == result
        get_response = client.get(f"/{prefix}/{id_}")
        assert 200 == get_response.status_code
        assert with_id == get_response.json()
        delete_response = client.delete(f"/{prefix}/{id_}")
        assert 200 == delete_response.status_code
        assert with_id == delete_response.json()
        assert 404 == client.get(f"/{prefix}/{id_}").status_code
