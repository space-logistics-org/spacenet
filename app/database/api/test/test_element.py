"""
Contains integration tests where CRUD operations are exercised with elements.
These integration tests must be run sequentially: at present they assume that the
database is empty before performing CRUD operations.
"""
import random
from contextlib import contextmanager
from enum import Enum
from typing import Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient
from hypothesis import assume, given, settings, strategies as st

from app.database.api.database import Base, get_db
from app.database.api.main import app
from app.database.api.models.element import Element as ElementModel
from app.database.test.utilities import test_engine
from app.auth_dependencies import current_user
from spacenet.schemas.element import ElementKind
from spacenet.schemas.test.test_element import (
    VALID_ELEMENT_MAP,
    VALID_ELEMENT_CARRIER_MAP,
    VALID_HUMAN_AGENT_MAP,
    VALID_ROBOTIC_AGENT_MAP,
    VALID_RESOURCE_CONTAINER_MAP,
    VALID_SURFACE_VEHICLE_MAP,
    VALID_PROPULSIVE_VEHICLE_MAP,
    INVALID_ELEMENT_MAP,
    INVALID_ROBOTIC_AGENT_MAP,
    INVALID_HUMAN_AGENT_MAP,
    INVALID_ELEMENT_CARRIER_MAP,
    INVALID_RESOURCE_CONTAINER_MAP,
    INVALID_SURFACE_VEHICLE_MAP,
    INVALID_PROPULSIVE_VEHICLE_MAP,
    kw_strategy_from_maps_and_param,
)
from .utilities import (
    filter_val_not_none,
    get_test_db,
    get_current_user,
    make_subset,
    with_type,
)

pytestmark = [pytest.mark.integration, pytest.mark.element, pytest.mark.routing]

client = TestClient(app)

Base.metadata.create_all(bind=test_engine)

app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[current_user] = get_current_user


def valid_invalid_strategies_from_maps(
    valid_map, invalid_map
) -> Tuple[st.SearchStrategy, st.SearchStrategy]:
    valid = st.fixed_dictionaries(valid_map)
    invalid = st.one_of(
        *(
            kw_strategy_from_maps_and_param(valid_map, invalid_map, invalid_param)
            for invalid_param in invalid_map
        )
    )
    return valid, invalid


def get_invalid_types(my_type: ElementKind) -> Tuple[ElementKind, ...]:
    """
    Get a list of all invalid type discriminants, given that the only valid type discriminant
    is the provided "myType".

    :param my_type: the valid type discriminant
    :return:  all invalid type discriminants
    """
    return tuple(kind for kind in ElementKind if kind != my_type)



def convert_enum_variants_to_values(v):
    return v.value if isinstance(v, Enum) else v


def equivalent_json(inp, response) -> bool:
    return {k: convert_enum_variants_to_values(v) for k, v in inp.items()} == {
        k: v for k, v in response.items() if k != "id"
    }


KIND_TO_STRATEGIES: Dict[ElementKind, Tuple[st.SearchStrategy, st.SearchStrategy]] = {
    ElementKind.Element: valid_invalid_strategies_from_maps(
        VALID_ELEMENT_MAP,
        dict(
            INVALID_ELEMENT_MAP,
            type=st.sampled_from(
                [
                    variant
                    for variant in ElementKind
                    if variant
                    not in {ElementKind.Element, ElementKind.ResourceContainer}
                ]
            ),
        ),
    ),
    ElementKind.ElementCarrier: valid_invalid_strategies_from_maps(
        VALID_ELEMENT_CARRIER_MAP, INVALID_ELEMENT_CARRIER_MAP
    ),
    ElementKind.ResourceContainer: valid_invalid_strategies_from_maps(
        VALID_RESOURCE_CONTAINER_MAP, INVALID_RESOURCE_CONTAINER_MAP
    ),
    ElementKind.RoboticAgent: valid_invalid_strategies_from_maps(
        VALID_ROBOTIC_AGENT_MAP,
        dict(
            INVALID_ROBOTIC_AGENT_MAP,
            type=st.sampled_from(
                [
                    variant
                    for variant in ElementKind
                    if variant not in {ElementKind.RoboticAgent, ElementKind.HumanAgent}
                ]
            ),
        ),
    ),
    ElementKind.HumanAgent: valid_invalid_strategies_from_maps(
        VALID_HUMAN_AGENT_MAP,
        dict(
            INVALID_HUMAN_AGENT_MAP,
            type=st.sampled_from(
                [
                    variant
                    for variant in ElementKind
                    if variant not in {ElementKind.RoboticAgent, ElementKind.HumanAgent}
                ]
            ),
        ),
    ),
    ElementKind.PropulsiveVehicle: valid_invalid_strategies_from_maps(
        VALID_PROPULSIVE_VEHICLE_MAP, INVALID_PROPULSIVE_VEHICLE_MAP
    ),
    ElementKind.SurfaceVehicle: valid_invalid_strategies_from_maps(
        VALID_SURFACE_VEHICLE_MAP, INVALID_SURFACE_VEHICLE_MAP
    ),
}

TESTED_VARIANTS: List[ElementKind] = [variant for variant in ElementKind]


@contextmanager
def clear_tables_scope():
    """Clear the database after a series of operations."""
    ElementModel.__table__.drop(test_engine, checkfirst=True)
    ElementModel.__table__.create(test_engine, checkfirst=False)
    try:
        yield
    finally:
        ElementModel.__table__.drop(test_engine, checkfirst=True)
        ElementModel.__table__.create(test_engine, checkfirst=False)


def test_empty():
    # GET LIST w/o a POST: should be no elements
    response = client.get("/element/")
    assert response.status_code == 200
    assert response.json() == []
    # GET w/o any elements: should 404
    response = client.get("/element/1")
    assert response.status_code == 404


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
@given(data=st.data())
@settings(max_examples=5)
def test_create(data: st.DataObject, element_type: ElementKind):
    with clear_tables_scope():
        valid_st, invalid_st = KIND_TO_STRATEGIES[element_type]
        # POST an invalid element: should 422
        invalid_kw = data.draw(invalid_st)
        assume(
            not element_type == ElementKind.Element
            or not invalid_kw["type"] == ElementKind.ResourceContainer
        )
        try:
            response = client.post("/element/", json=invalid_kw)
        except ValueError:
            assert {float("inf"), -float("inf")} & set(invalid_kw.values())
        else:
            assert (
                response.status_code == 422
            ), f"should have failed but got {response.json()}"
        # POST a valid element: should 201
        valid_kw = data.draw(valid_st)
        post_response = client.post("/element/", json=valid_kw)
        assert post_response.status_code == 201
        assert equivalent_json(valid_kw, post_response.json())
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
@given(data=st.data())
@settings(max_examples=5)
def test_update(data: st.DataObject, element_type: ElementKind):
    def check_get():
        get_r = client.get(f"/element/{id_}")
        assert get_r.status_code == 200
        assert expected_fields == get_r.json()

    with clear_tables_scope():
        valid_st, invalid_st = KIND_TO_STRATEGIES[element_type]
        kw = data.draw(valid_st)
        post_r = client.post("/element/", json=kw)
        assert post_r.status_code == 201
        id_ = post_r.json()["id"]
        # PATCH that element w/ valid inputs: should be a 200
        patch_kw = with_type(make_subset(data.draw(valid_st)), element_type)
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
        valid_other_st, _ = KIND_TO_STRATEGIES[other_type]
        non_matching_kw = data.draw(valid_other_st)
        bad_patch = client.patch(f"/element/{id_}", json=non_matching_kw)
        assert bad_patch.status_code == 409
        # GET that element: should not have changed
        check_get()
        # PATCH the element with invalid schema: should be a 422
        invalid_kw = data.draw(invalid_st)
        assume(invalid_kw["type"] == element_type)
        # if the type here is the conflict this can fail, as then invalid_kw should raise a 409
        try:
            bad_patch = client.patch(f"/element/{id_}", json=invalid_kw)
        except ValueError:
            assert {float("inf"), -float("inf")} & set(invalid_kw.values())
        else:
            assert bad_patch.status_code == 422
        # GET that element: should not have changed
        check_get()


@pytest.mark.parametrize("element_type", TESTED_VARIANTS)
@given(data=st.data())
@settings(max_examples=5)
def test_delete(data: st.DataObject, element_type: ElementKind):
    def check_get_all():
        read_all_r = client.get("/element/")
        assert read_all_r.status_code == 200
        for v in read_all_r.json():
            assert v in posted_vals
        for v in posted_vals:
            assert v in read_all_r.json()

    with clear_tables_scope():
        # POST 2 valid elements
        num_posts = 2
        posted_vals = []
        valid_st, _ = KIND_TO_STRATEGIES[element_type]
        for _ in range(num_posts):
            valid_kw = data.draw(valid_st)
            post_r = client.post("/element/", json=valid_kw)
            assert post_r.status_code == 201
            assert equivalent_json(valid_kw, post_r.json())
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
