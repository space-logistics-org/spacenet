"""
Contains integration tests where CRUD operations are exercised with nodes and edges,
methodologically similar to element routing testing. Same restrictions on sequential runs
only apply.
"""
import json
import random
from enum import Enum
from typing import List, Type

import pkg_resources
import pytest
from fastapi.testclient import TestClient

import spacenet
from app.database.api.database import Base, get_db
from app.database.api.main import app
from app.database.api.models.edge import Edge as EdgeModel
from app.database.api.models.node import Node as NodeModel
from app.database.test.utilities import test_engine
from spacenet.schemas.edge import EdgeType
from spacenet.schemas.node import NodeType
from .utilities import (
    filter_val_not_none,
    first_subset_second,
    get_test_db,
    make_subset,
)

pytestmark = [pytest.mark.integration, pytest.mark.routing]

client = TestClient(app)

app.dependency_overrides[get_db] = get_test_db


Base.metadata.create_all(bind=test_engine)

GOOD_NODE_LIST = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/good_nodes.json")
)

BAD_NODE_LIST = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/bad_nodes.json")
)

GOOD_EDGE_LIST = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/good_edges.json")
)

BAD_EDGE_LIST = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/bad_edges.json")
)


def get_other_variants(to_exclude, enum: Type[Enum]) -> List[Enum]:
    return [variant.value for variant in enum if variant != to_exclude]


NODE_PREFIX = "/node"
EDGE_PREFIX = "/edge"

NODE_VARIANTS = [variant for variant in NodeType]
EDGE_VARIANTS = [variant for variant in EdgeType]
NODE_NAMES = list(map(str, NODE_VARIANTS))
EDGE_NAMES = list(map(str, EDGE_VARIANTS))
NAMES_TO_VALUES = {
    **{str(variant): variant.value for variant in NODE_VARIANTS},
    **{str(variant): variant.value for variant in EDGE_VARIANTS},
}
NAMES_TO_VARIANTS = {
    **{str(variant): variant for variant in NODE_VARIANTS},
    **{str(variant): variant for variant in EDGE_VARIANTS},
}

GOOD_NODES = {
    variant.value: [obj for obj in GOOD_NODE_LIST if obj["type"] == variant.value]
    for variant in NODE_VARIANTS
}
GOOD_EDGES = {
    variant.value: [obj for obj in GOOD_EDGE_LIST if obj["type"] == variant.value]
    for variant in EDGE_VARIANTS
}


def name_to_obj(name):
    assert name in NODE_NAMES or name in EDGE_NAMES
    return (
        (GOOD_NODES, BAD_NODE_LIST)
        if name in NODE_NAMES
        else (GOOD_EDGES, BAD_EDGE_LIST)
    )


NAMES_TO_OBJECTS = {
    name: name_to_obj(name)
    for name in [str(variant) for variant in NODE_VARIANTS + EDGE_VARIANTS]
}

VARIANT_NAME_TO_PREFIX = {
    name: NODE_PREFIX if name in NODE_NAMES else EDGE_PREFIX
    for name in NODE_NAMES + EDGE_NAMES
}


@pytest.fixture(scope="module")
def seed_and_make_tables():
    random.seed("spacenet")
    NodeModel.__table__.create(test_engine)
    EdgeModel.__table__.create(test_engine)
    yield
    NodeModel.__table__.drop(test_engine)
    EdgeModel.__table__.drop(test_engine)


@pytest.fixture(autouse=True)
def reseed_and_clear_tables():
    random.seed("spacenet")
    EdgeModel.__table__.drop(test_engine, checkfirst=False)
    NodeModel.__table__.drop(test_engine)
    EdgeModel.__table__.create(test_engine, checkfirst=True)
    NodeModel.__table__.create(test_engine)


@pytest.mark.parametrize(
    "prefix",
    [
        pytest.param(NODE_PREFIX, marks=pytest.mark.node),
        pytest.param(EDGE_PREFIX, marks=pytest.mark.edge),
    ],
)
def test_empty(prefix):
    read_all_response = client.get(prefix)
    assert read_all_response.status_code == 200
    assert read_all_response.json() == []
    read_response = client.get(f"{prefix}1")
    assert read_response.status_code == 404


@pytest.mark.parametrize(
    "variant_name",
    [pytest.param(name, marks=[pytest.mark.node,],) for name in NODE_NAMES]
    + [pytest.param(name, marks=[pytest.mark.edge,],) for name in EDGE_NAMES],
)
def test_create(variant_name):
    prefix = VARIANT_NAME_TO_PREFIX[variant_name]
    all_good_values, bad_values = NAMES_TO_OBJECTS[variant_name]
    value = NAMES_TO_VALUES[variant_name]
    good_values = all_good_values[value]
    bad_response = client.post(f"{prefix}/", json=random.choice(bad_values))
    assert bad_response.status_code == 422
    good_val = random.choice(good_values)
    post_response = client.post(f"{prefix}/", json=good_val)
    assert post_response.status_code == 201, f"failed for {good_val}"
    assert first_subset_second(good_val, post_response.json())
    assert len(good_val) == len(post_response.json()) - 1
    id_ = post_response.json()["id"]
    read_response = client.get(f"{prefix}/{id_}")
    assert read_response.status_code == 200
    assert read_response.json() == post_response.json()
    read_all_response = client.get(f"{prefix}/")
    assert read_all_response.status_code == 200
    assert len(read_all_response.json()) == 1
    assert read_all_response.json()[0] == read_response.json()


@pytest.mark.parametrize(
    "variant_name",
    [pytest.param(name, marks=[pytest.mark.node,],) for name in NODE_NAMES]
    + [pytest.param(name, marks=[pytest.mark.edge,],) for name in EDGE_NAMES],
)
def test_update(variant_name):
    def check_get():
        get_r = client.get(f"{prefix}/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    prefix = VARIANT_NAME_TO_PREFIX[variant_name]
    all_good_values, bad_values = NAMES_TO_OBJECTS[variant_name]
    value = NAMES_TO_VALUES[variant_name]
    good_values = all_good_values[value]
    first_good = good_values[0]
    second_good = random.choice(good_values[1:])
    kw = first_good
    post_r = client.post(f"{prefix}/", json=kw)
    assert post_r.status_code == 201
    id_ = post_r.json()["id"]
    patch_kw = make_subset(second_good)
    patch_r = client.patch(f"{prefix}/{id_}", json=patch_kw)
    assert patch_r.status_code == 200
    expected_fields = {**kw, **filter_val_not_none(patch_kw), "id": id_}
    assert expected_fields == patch_r.json()
    check_get()
    not_present_id = id_ + 1
    bad_patch = client.patch(f"{prefix}/{not_present_id}", json=patch_kw)
    assert bad_patch.status_code == 404
    check_get()
    variant = NAMES_TO_VARIANTS[variant_name]
    parent_enum = NodeType if variant_name in NODE_NAMES else EdgeType
    other_variant = random.choice(get_other_variants(variant, parent_enum))
    mistyped = random.choice(all_good_values[other_variant])
    # variant to all other
    bad_patch = client.patch(f"{prefix}/{id_}", json=mistyped)
    assert bad_patch.status_code == 409
    check_get()
    invalid_kw = random.choice(bad_values)
    bad_patch = client.patch(f"{prefix}/{id_}", json=invalid_kw)
    assert bad_patch.status_code == 422
    check_get()


@pytest.mark.parametrize(
    "variant_name",
    [pytest.param(name, marks=[pytest.mark.node,],) for name in NODE_NAMES]
    + [pytest.param(name, marks=[pytest.mark.edge,],) for name in EDGE_NAMES],
)
def test_delete(variant_name):
    def check_get_all():
        read_all_r = client.get(f"{prefix}/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_values
        for v in posted_values:
            assert v in read_all_r.json()

    prefix = VARIANT_NAME_TO_PREFIX[variant_name]
    all_good_values, bad_values = NAMES_TO_OBJECTS[variant_name]
    value = NAMES_TO_VALUES[variant_name]
    good_values = all_good_values[value]
    posted_values = []
    first_good, second_good = good_values[0], random.choice(good_values[1:])
    for i in range(2):
        valid_kw = first_good if i == 0 else second_good
        post_r = client.post(f"{prefix}/", json=valid_kw)
        assert post_r.status_code == 201
        assert first_subset_second(valid_kw, post_r.json())
        posted_values.append({**valid_kw, "id": post_r.json()["id"]})
    check_get_all()
    to_delete = posted_values.pop()
    del_r = client.delete(f"{prefix}/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    check_get_all()
    del_r = client.delete(f"{prefix}/{to_delete['id']}")
    assert del_r.status_code == 404
    del_r = client.delete(f"{prefix}/{to_delete['id'] + 1000}")
    assert del_r.status_code == 404
    check_get_all()
    to_delete = posted_values.pop()
    del_r = client.delete(f"{prefix}/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    read_all_r = client.get(f"{prefix}/")
    assert read_all_r.status_code == 200
    assert len(read_all_r.json()) == 0
