"""
Contains integration tests where CRUD operations are exercised with edges, methodologically
similar to element routing testing. Same restrictions on sequential runs only apply.
"""
import json
import random
from typing import List

import pkg_resources
import pytest
from fastapi.testclient import TestClient

import spacenet
from spacenet.schemas.edge import EdgeType
from .utilities import (
    TestingSessionLocal,
    filter_val_not_none,
    first_subset_second,
    make_subset,
    test_engine,
    with_type,
)
from ..api.database import Base, get_db
from ..api.main import app
from ..api.models.edge import Edge as EdgeModel

pytestmark = [pytest.mark.integration, pytest.mark.edge]

client = TestClient(app)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

ALL_VARIANTS = [EdgeType.Surface, EdgeType.Space, EdgeType.Flight]

TESTED_VARIANTS: List[EdgeType] = ALL_VARIANTS

GOOD_EDGES = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/goodEdges.json")
)

BAD_EDGES = json.loads(
    pkg_resources.resource_string(spacenet.__name__, "test/badEdges.json")
)


def get_invalid_types(edge_type: EdgeType) -> List[EdgeType]:
    return [variant for variant in ALL_VARIANTS if variant != edge_type]


MISTYPED_EDGES = [
    {**good_edge, "type": get_invalid_types(good_edge["type"])[0]}
    for good_edge in GOOD_EDGES
]


@pytest.fixture(scope="module")
def edge_routing():
    random.seed("spacenet")
    EdgeModel.__table__.create(test_engine)
    yield
    EdgeModel.__table__.drop(test_engine)


@pytest.fixture(autouse=True)
def reseed_and_clear_tables():
    random.seed("spacenet")
    EdgeModel.__table__.drop(test_engine, checkfirst=False)
    EdgeModel.__table__.create(test_engine, checkfirst=True)


@pytest.mark.parametrize("edge_type", TESTED_VARIANTS)
def test_empty(edge_type: EdgeType):
    read_all_response = client.get("/edge/")
    assert read_all_response.status_code == 200
    assert read_all_response.json() == []
    read_response = client.get("/edge/1")
    assert read_response.status_code == 404


@pytest.mark.parametrize("edge_type", TESTED_VARIANTS)
def test_create(edge_type: EdgeType):
    bad_response = client.post("/edge/", json=random.choice(BAD_EDGES))
    assert bad_response.status_code == 422
    good_edge = random.choice(GOOD_EDGES)
    post_response = client.post("/edge/", json=good_edge)
    assert post_response.status_code == 201
    assert first_subset_second(good_edge, post_response.json())
    assert len(good_edge) == len(post_response.json()) - 1
    id_ = post_response.json()["id"]
    read_response = client.get(f"/edge/{id_}")
    assert read_response.status_code == 200
    assert read_response.json() == post_response.json()
    read_all_response = client.get("/edge/")
    assert read_all_response.status_code == 200
    assert len(read_all_response.json()) == 1
    assert read_all_response.json()[0] == read_response.json()


@pytest.mark.parametrize("edge_type", TESTED_VARIANTS)
def test_update(edge_type: EdgeType):
    def check_get():
        get_r = client.get(f"/edge/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    first_good = GOOD_EDGES[0]
    second_good = random.choice(GOOD_EDGES[1:])
    kw = with_type(first_good, edge_type)
    post_r = client.post("/edge/", json=kw)
    assert post_r.status_code == 201
    id_ = post_r.json()["id"]
    patch_kw = with_type(make_subset(second_good), edge_type.value)
    patch_r = client.patch(f"/edge/{id_}", json=patch_kw)
    assert patch_r.status_code == 200
    expected_fields = {**kw, **filter_val_not_none(patch_kw), "id": id_}
    assert expected_fields == patch_r.json()
    check_get()
    not_present_id = id_ + 1
    bad_patch = client.patch(f"/edge/{not_present_id}", json=patch_kw)
    assert bad_patch.status_code == 404
    check_get()
    other_type = (
        EdgeType.discrete if edge_type == EdgeType.continuous else EdgeType.continuous
    )
    mistyped = random.choice(MISTYPED_EDGES)
    non_matching_kw = with_type(mistyped, other_type)
    bad_patch = client.patch(f"/edge/{id_}", json=non_matching_kw)
    assert bad_patch.status_code == 409
    check_get()
    invalid_kw = with_type(random.choice(BAD_EDGES), edge_type)
    bad_patch = client.patch(f"/edge/{id_}", json=invalid_kw)
    assert bad_patch.status_code == 422
    check_get()


@pytest.mark.parametrize("edge_type", TESTED_VARIANTS)
def test_delete(edge_type: EdgeType):
    def check_get_all():
        read_all_r = client.get("/edge/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_vals
        for v in posted_vals:
            assert v in read_all_r.json()

    posted_vals = []
    first_good, second_good = GOOD_EDGES[1], random.choice(GOOD_EDGES[2:])
    for i in range(2):
        # first, second, _, _ = KIND_TO_ARGS[edge_type]
        base_kw = first_good if i == 0 else second_good
        valid_kw = with_type(base_kw, edge_type)
        post_r = client.post("/edge/", json=valid_kw)
        assert post_r.status_code == 201
        assert first_subset_second(valid_kw, post_r.json())
        posted_vals.append({**valid_kw, "id": post_r.json()["id"]})
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/edge/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    check_get_all()
    del_r = client.delete(f"/edge/{to_delete['id']}")
    assert del_r.status_code == 404
    del_r = client.delete(f"/edge/{to_delete['id'] + 1000}")
    assert del_r.status_code == 404
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/edge/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    read_all_r = client.get("/edge/")
    assert read_all_r.status_code == 200
    assert len(read_all_r.json()) == 0


if __name__ == "__main__":
    pytest.main()
