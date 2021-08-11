import pytest
from fastapi.testclient import TestClient

from app.database.api.database import get_db
from app.database.api.main import app
from app.auth_dependencies import current_user
from ..schemas.constants import CREATE_SCHEMAS
from app.database.api.test.utilities import get_current_user, get_test_db
from spacenet.schemas.element import Element
from spacenet.schemas.node import Node
from spacenet.schemas.edge import Edge
from spacenet.schemas.resource import Resource
from spacenet.schemas.test.utilities import (
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
    for super_ in (Element, Node, Edge, Resource):
        if issubclass(type_, super_):
            return super_


TYPE_TO_SUPER = {cls: schema_superclass(cls) for cls in CREATE_SCHEMAS}


SUPER_TO_PREFIX = {Element: "element", Edge: "edge", Node: "node", Resource: "resource"}


def object_to_prefix(obj: dict) -> str:
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
