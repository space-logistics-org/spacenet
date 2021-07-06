"""
Contains integration tests where CRUD operations are exercised with elements. Uses equivalence
partitioning. These integration tests must be run sequentially: at present they assume that the
database is empty before performing CRUD operations.

For each Element type:
    GET:
        Partition on expected return code:
            - 200 (ID exists)
            - 404 (no such ID)
    GET LIST:
        Partition on expected number of list elements
            - expecting 0 elements
            - expecting 1 element
            - expecting > 1 element
    POST:
        Partition on expected return code:
            - 201 (valid inputs)
            - 422 (invalid inputs)
    PATCH:
        Partition on expected return code:
            - 200 (valid inputs, matching type, ID exists)
            - 404 (no such ID)
            - 409 (the element with this ID has non-matching type)
            - 422 (invalid inputs)
    DELETE:
        Partition on expected return code:
            - 200 (ID exists)
            - 404 (no such ID)
"""
import random
from typing import Dict, List, Tuple, Type

import pytest
from fastapi.testclient import TestClient

from app.database.api.database import Base, get_db
from app.database.api.main import app
from app.database.api.models.element import Element as ElementModel
from app.database.test.utilities import test_engine
from spacenet.schemas.element import ElementKind
from spacenet.test.element_factories import *
from .utilities import (
    filter_val_not_none,
    first_subset_second,
    get_test_db,
    make_subset,
    with_type,
)

pytestmark = [pytest.mark.integration, pytest.mark.element, pytest.mark.routing]

client = TestClient(app)

Base.metadata.create_all(bind=test_engine)


app.dependency_overrides[get_db] = get_test_db

KIND_TO_FACTORIES: Dict[
    ElementKind, Tuple[Type[ValidArgsFactory], Type[InvalidArgsFactory]]
] = {
    ElementKind.Element: (ValidElementArgsFactory, InvalidElementArgsFactory),
    ElementKind.ElementCarrier: (
        ValidElementCarrierArgsFactory,
        InvalidElementCarrierArgsFactory,
    ),
    ElementKind.ResourceContainer: (
        ValidCargoCarrierArgsFactory,
        InvalidCargoCarrierArgsFactory,
    ),
    ElementKind.RoboticAgent: (ValidAgentArgsFactory, InvalidAgentArgsFactory),
    ElementKind.HumanAgent: (ValidAgentArgsFactory, InvalidAgentArgsFactory),
    ElementKind.PropulsiveVehicle: (ValidPropulsiveArgsFactory, InvalidPropulsiveArgsFactory),
    ElementKind.SurfaceVehicle: (ValidSurfaceArgsFactory, InvalidSurfaceArgsFactory),
}

TESTED_VARIANTS: List[ElementKind] = [variant for variant in ElementKind]


@pytest.fixture(scope="module")
def element_routing():
    ElementModel.__table__.create(test_engine)
    random.seed("spacenet")
    yield
    ElementModel.__table__.drop(test_engine)


@pytest.fixture(autouse=True)
def reseed_and_clear_tables():
    ElementModel.__table__.drop(test_engine, checkfirst=False)
    ElementModel.__table__.create(test_engine, checkfirst=True)
    random.seed("spacenet")


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
def test_empty(element_type: ElementKind):
    # GET LIST w/o a POST: should be no elements
    response = client.get("/element/")
    assert response.status_code == 200
    assert response.json() == []
    # GET w/o any elements: should 404
    response = client.get("/element/1")
    assert response.status_code == 404


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
def test_create(element_type: ElementKind):
    valid_factory, invalid_factory = KIND_TO_FACTORIES[element_type]
    # POST an invalid element: should 422
    invalid_kw = invalid_factory.make_keywords()
    response = client.post("/element/", json=invalid_kw)
    assert response.status_code == 422
    # POST a valid element: should 201
    valid_kw = with_type(valid_factory.make_keywords(), element_type)
    post_response = client.post("/element/", json=valid_kw)
    assert post_response.status_code == 201
    assert first_subset_second(valid_kw, post_response.json())
    assert len(valid_kw) == len(post_response.json()) - 1
    id_ = post_response.json()["id"]
    # GET that element: should be a 200 and have correct values
    read_response = client.get(f"/element/{id_}")
    assert read_response.status_code == 200
    assert read_response.json() == post_response.json()
    # GET LIST: should have 1 element
    read_all_response = client.get(f"/element/")
    assert read_all_response.status_code == 200
    assert (
        len(read_all_response.json()) == 1
    ), "expected length-1 list of existing elements"
    assert read_response.json() == read_all_response.json()[0]


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
def test_update(element_type: ElementKind):
    def check_get():
        get_r = client.get(f"/element/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    valid_factory, invalid_factory = KIND_TO_FACTORIES[element_type]
    kw = with_type(valid_factory.make_keywords(), element_type)
    post_r = client.post("/element/", json=kw)
    assert post_r.status_code == 201
    id_ = post_r.json()["id"]
    # PATCH that element w/ valid inputs: should be a 200
    patch_kw = with_type(make_subset(valid_factory.make_keywords()), element_type)
    patch_r = client.patch(f"/element/{id_}", json=patch_kw)
    assert patch_r.status_code == 200
    expected_fields = {**kw, **filter_val_not_none(patch_kw), "id": id_}
    assert expected_fields == patch_r.json()
    # GET that element: should match new vals
    check_get()
    # PATCH an element not in the database: should be a 404
    not_present_id = id_ + 1
    bad_patch = client.patch(f"/element/{not_present_id}", json=patch_kw)
    assert bad_patch.status_code == 404
    # GET that element: should not have changed
    check_get()
    # PATCH the element with non-matching type but valid schema: should be a 409
    other_type = random.choice(get_invalid_types(element_type))
    valid_other, _ = KIND_TO_FACTORIES[other_type]
    non_matching_kw = with_type(valid_other.make_keywords(), other_type)
    bad_patch = client.patch(f"/element/{id_}", json=non_matching_kw)
    assert bad_patch.status_code == 409
    # GET that element: should not have changed
    check_get()
    # PATCH the element with invalid schema: should be a 422
    invalid_kw = with_type(invalid_factory.make_keywords(), element_type)
    bad_patch = client.patch(f"/element/{id_}", json=invalid_kw)
    assert bad_patch.status_code == 422
    # GET that element: should not have changed
    check_get()


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
def test_delete(element_type: ElementKind):
    def check_get_all():
        read_all_r = client.get("/element/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_vals
        for v in posted_vals:
            assert v in read_all_r.json()

    # POST 2 valid elements
    num_posts = 2
    posted_vals = []
    for _ in range(num_posts):
        valid_factory, invalid_factory = KIND_TO_FACTORIES[element_type]
        valid_kw = with_type(valid_factory.make_keywords(), element_type)
        post_r = client.post("/element/", json=valid_kw)
        assert post_r.status_code == 201
        assert first_subset_second(valid_kw, post_r.json())
        posted_vals.append({**valid_kw, "id": post_r.json()["id"]})
    # GET LIST and check that both are present
    check_get_all()
    # DELETE an element: should be a 200
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/element/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    # GET LIST and check that only 1 is present
    check_get_all()
    # DELETE the same ID: should be a 404
    del_r = client.delete(f"/element/{to_delete['id']}")
    assert del_r.status_code == 404
    # DELETE a different ID: should be a 404
    del_r = client.delete(f"/element/{to_delete['id'] + 1000}")
    assert del_r.status_code == 404
    # GET LIST and check that only 1 is present
    check_get_all()
    # DELETE the remaining element: should be a 200
    to_delete = posted_vals.pop()
    del_r = client.delete(f"/element/{to_delete['id']}")
    assert del_r.status_code == 200
    assert del_r.json() == to_delete
    # GET LIST and check that is empty
    read_all_r = client.get("/element/")
    assert read_all_r.status_code == 200
    assert len(read_all_r.json()) == 0


if __name__ == "__main__":
    pytest.main()
