import json
import random
from typing import List

import pkg_resources
import pytest
from fastapi.testclient import TestClient

import spacenet
from app.database.api.database import Base, get_db
from spacenet.schemas.node import NodeType
from .utilities import (
    TestingSessionLocal,
    filter_val_not_none,
    first_subset_second,
    make_subset,
    test_engine,
    with_type,
)
from ..api.main import app
from ..api.models.node import Node as NodeModel

pytestmark = [pytest.mark.integration, pytest.mark.node]

client = TestClient(app)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

ALL_VARIANTS = [NodeType.Surface, NodeType.Orbital, NodeType.Lagrange]

TESTED_VARIANTS: List[NodeType] = ALL_VARIANTS

GOOD_NODES = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/goodNodes.json")
)

BAD_NODES = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/badNodes.json")
)


def get_invalid_types(node_type: NodeType) -> List[NodeType]:
    return [variant for variant in ALL_VARIANTS if variant != node_type]


MISTYPED_NODES = [
    {**good_node, "type": get_invalid_types(good_node["type"])[0]}
    for good_node in GOOD_NODES
]


@pytest.fixture(scope="module")
def node_routing():
    random.seed("spacenet")
    NodeModel.__table__.create(test_engine)
    yield
    NodeModel.__table__.drop(test_engine)


@pytest.fixture(autouse=True)
def reseed_and_clear_tables():
    random.seed("spacenet")
    NodeModel.__table__.drop(test_engine, checkfirst=False)
    NodeModel.__table__.create(test_engine, checkfirst=True)


@pytest.mark.parametrize("node_type", TESTED_VARIANTS)
def test_empty(node_type: NodeType):
    read_all_response = client.get("/node/")
    assert read_all_response.status_code == 200
    assert read_all_response.json() == []
    read_response = client.get("/node/1")
    assert read_response.status_code == 404


@pytest.mark.parametrize(
    "node_type", [NodeType.Surface, NodeType.Orbital, NodeType.Lagrange]
)
def test_create(node_type: NodeType):
    bad_response = client.post("/node/", json=random.choice(BAD_NODES))
    assert bad_response.status_code == 422
    good_input = random.choice(GOOD_NODES)
    post_response = client.post("/node/", json=good_input)
    assert post_response.status_code == 201
    assert first_subset_second(good_input, post_response.json())
    assert len(good_input) == len(post_response.json()) - 1
    id_ = post_response.json()["id"]
    read_response = client.get(f"/node/{id_}")
    assert read_response.status_code == 200
    assert read_response.json() == post_response.json()
    read_all_response = client.get("/node/")
    assert read_all_response.status_code == 200
    assert len(read_all_response.json()) == 1
    assert read_all_response.json()[0] == read_response.json()


@pytest.mark.parametrize("node_type", TESTED_VARIANTS)
def test_update(node_type: NodeType):
    def check_get():
        get_r = client.get(f"/node/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    first_good = GOOD_NODES[0]
    second_good = random.choice(GOOD_NODES[1:])
    kw = with_type(first_good, node_type)
    post_r = client.post("/node/", json=kw)
    assert post_r.status_code == 201
    id_ = post_r.json()["id"]
    patch_kw = with_type(make_subset(second_good), node_type.value)
    patch_r = client.patch(f"/node/{id_}", json=patch_kw)
    assert patch_r.status_code == 200
    expected_fields = {**kw, **filter_val_not_none(patch_kw), "id": id_}
    assert expected_fields == patch_r.json()
    check_get()
    not_present_id = id_ + 1
    bad_patch = client.patch(f"/node/{not_present_id}", json=patch_kw)
    assert bad_patch.status_code == 404
    check_get()
    other_type = (
        NodeType.discrete if node_type == NodeType.continuous else NodeType.continuous
    )
    mistyped = random.choice(MISTYPED_NODES)
    non_matching_kw = with_type(mistyped, other_type)
    bad_patch = client.patch(f"/node/{id_}", json=non_matching_kw)
    assert bad_patch.status_code == 409
    check_get()
    invalid_kw = with_type(random.choice(BAD_NODES), node_type)
    bad_patch = client.patch(f"/node/{id_}", json=invalid_kw)
    assert bad_patch.status_code == 422
    check_get()


@pytest.mark.parametrize("node_type", TESTED_VARIANTS)
def test_delete(node_type: NodeType):
    def check_get_all():
        read_all_r = client.get("/node/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_vals
        for v in posted_vals:
            assert v in read_all_r.json()

    posted_vals = []
    first_good, second_good = GOOD_NODES[1], random.choice(GOOD_NODES[2:])
    for i in range(2):
        # first, second, _, _ = KIND_TO_ARGS[node_type]
        base_kw = first_good if i == 0 else second_good
        valid_kw = with_type(base_kw, node_type)
        post_r = client.post("/node/", json=valid_kw)
        assert post_r.status_code == 201
        assert first_subset_second(valid_kw, post_r.json())
        posted_vals.append({**valid_kw, "id": post_r.json()["id"]})
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/node/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    check_get_all()
    del_r = client.delete(f"/node/{to_delete['id']}")
    assert del_r.status_code == 404
    del_r = client.delete(f"/node/{to_delete['id'] + 1000}")
    assert del_r.status_code == 404
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/node/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    read_all_r = client.get("/node/")
    assert read_all_r.status_code == 200
    assert len(read_all_r.json()) == 0


if __name__ == "__main__":
    pytest.main()
