"""
Contains integration tests where CRUD operations are exercised with resources, methodologically
similar to element routing testing. Same restrictions on sequential runs only apply.
"""
from typing import Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spacenet.schemas.resource import ResourceType
from .utilities import filter_val_not_none, first_subset_second, make_subset, with_type
from ..api.database import Base, get_db
from ..api.models.resource import Resource as ResourceModel
from ..api.main import app

pytestmark = [pytest.mark.integration, pytest.mark.resource]

client = TestClient(app)

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

VALID_DISCRETE_ARGS = {
    "name": "foo",
    "cos": 1,
    "type": "discrete",
    "unit_mass": 10,
    "unit_volume": 20,
    "description": "baz",
    "units": "kg",
}

OTHER_VALID_DISCRETE_ARGS = {
    **VALID_DISCRETE_ARGS,
    "unit_mass": 20,
    "unit_volume": 30,
    "cos": 2,
}

VALID_CONT_ARGS = {
    **VALID_DISCRETE_ARGS,
    "type": "continuous",
    "unit_mass": 10.2,
    "unit_volume": 24.1,
}

OTHER_VALID_CONT_ARGS = {
    **VALID_CONT_ARGS,
    "unit_mass": 20.5,
    "unit_volume": 30.15,
    "cos": 2,
}

INVALID_DISCRETE_ARGS = {**VALID_DISCRETE_ARGS, "cos": 99999}

MISTYPED_DISCRETE_ARGS = {**VALID_CONT_ARGS, "unit_mass": 10, "unit_volume": 20}

INVALID_CONT_ARGS = {**VALID_CONT_ARGS, "cos": -10}

MISTYPED_CONT_ARGS = {**VALID_DISCRETE_ARGS, "unit_mass": 10.2, "unit_volume": 24.1}

KIND_TO_ARGS: Dict[ResourceType, Tuple[Dict, Dict, Dict, Dict]] = {
    ResourceType.discrete: (
        VALID_DISCRETE_ARGS,
        OTHER_VALID_DISCRETE_ARGS,
        INVALID_DISCRETE_ARGS,
        MISTYPED_DISCRETE_ARGS,
    ),
    ResourceType.continuous: (
        VALID_CONT_ARGS,
        OTHER_VALID_CONT_ARGS,
        INVALID_CONT_ARGS,
        MISTYPED_CONT_ARGS,
    ),
}

TESTED_VARIANTS: List[ResourceType] = [ResourceType.discrete, ResourceType.continuous]


@pytest.fixture(scope="module")
def resource_routing():
    ResourceModel.__table__.create(engine)
    yield
    ResourceModel.__table__.drop(engine)


@pytest.fixture(autouse=True)
def clear_tables():
    ResourceModel.__table__.drop(engine, checkfirst=False)
    ResourceModel.__table__.create(engine, checkfirst=True)


@pytest.mark.parametrize("resource_type", TESTED_VARIANTS)
def test_empty(resource_type: ResourceType):
    read_all_response = client.get("/resource/")
    assert read_all_response.status_code == 200
    assert read_all_response.json() == []
    read_response = client.get("/resource/1")
    assert read_response.status_code == 404


@pytest.mark.parametrize("resource_type", TESTED_VARIANTS)
def test_create(resource_type: ResourceType):
    first, _, invalid, _ = KIND_TO_ARGS[resource_type]
    bad_response = client.post("/resource/", json=invalid)
    assert bad_response.status_code == 422
    post_response = client.post("/resource/", json=first)
    assert post_response.status_code == 201
    assert first_subset_second(first, post_response.json())
    assert len(first) == len(post_response.json()) - 1
    id_ = post_response.json()["id"]
    read_response = client.get(f"/resource/{id_}")
    assert read_response.status_code == 200
    assert read_response.json() == post_response.json()
    read_all_response = client.get("/resource/")
    assert read_all_response.status_code == 200
    assert len(read_all_response.json()) == 1
    assert read_all_response.json()[0] == read_response.json()


@pytest.mark.parametrize("resource_type", TESTED_VARIANTS)
def test_update(resource_type: ResourceType):
    def check_get():
        get_r = client.get(f"/resource/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    first, second, invalid, mistyped = KIND_TO_ARGS[resource_type]
    kw = with_type(first, resource_type)
    post_r = client.post("/resource/", json=kw)
    assert post_r.status_code == 201
    id_ = post_r.json()["id"]
    patch_kw = with_type(make_subset(second), resource_type.value)
    patch_r = client.patch(f"/resource/{id_}", json=patch_kw)
    assert patch_r.status_code == 200
    expected_fields = {**kw, **filter_val_not_none(patch_kw), "id": id_}
    assert expected_fields == patch_r.json()
    check_get()
    not_present_id = id_ + 1
    bad_patch = client.patch(f"/resource/{not_present_id}", json=patch_kw)
    assert bad_patch.status_code == 404
    check_get()
    other_type = (
        ResourceType.discrete
        if resource_type == ResourceType.continuous
        else ResourceType.continuous
    )
    non_matching_kw = with_type(mistyped, other_type)
    bad_patch = client.patch(f"/resource/{id_}", json=non_matching_kw)
    assert bad_patch.status_code == 409
    check_get()
    invalid_kw = with_type(invalid, resource_type)
    bad_patch = client.patch(f"/resource/{id_}", json=invalid_kw)
    assert bad_patch.status_code == 422
    check_get()


@pytest.mark.parametrize("resource_type", TESTED_VARIANTS)
def test_delete(resource_type: ResourceType):
    def check_get_all():
        read_all_r = client.get("/resource/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_vals
        for v in posted_vals:
            assert v in read_all_r.json()

    posted_vals = []
    for i in range(2):
        first, second, _, _ = KIND_TO_ARGS[resource_type]
        base_kw = first if i == 0 else second
        valid_kw = with_type(base_kw, resource_type)
        post_r = client.post("/resource/", json=valid_kw)
        assert post_r.status_code == 201
        assert first_subset_second(valid_kw, post_r.json())
        posted_vals.append({**valid_kw, "id": post_r.json()["id"]})
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/resource/{to_delete['id']}")
    assert del_r.status_code == 200
    check_get_all()
    del_r = client.delete(f"/resource/{to_delete['id']}")
    assert del_r.status_code == 404
    del_r = client.delete(f"/resource/{to_delete['id'] + 1000}")
    assert del_r.status_code == 404
    check_get_all()
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/resource/{to_delete['id']}")
    assert del_r.status_code == 200
    read_all_r = client.get("/resource/")
    assert read_all_r.status_code == 200
    assert len(read_all_r.json()) == 0


if __name__ == "__main__":
    pytest.main()
