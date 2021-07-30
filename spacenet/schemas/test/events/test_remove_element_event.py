import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import RemoveElements
from .utilities import EVENT_VALID_MAP, EVENT_INVALID_MAP
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    valid_invalid_from_allowed,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

ALLOWED_REMOVAL_POINTS = ["Node", "Edge"]
VALID_REMOVALS, INVALID_REMOVALS = valid_invalid_from_allowed(ALLOWED_REMOVAL_POINTS)
VALID_TYPES, INVALID_TYPES = valid_invalid_from_allowed(["RemoveElements"])

VALID_MAP = {
    "elements": st.lists(
        st.uuids()
    ),
    "removal_point_id": st.uuids(),
    **EVENT_VALID_MAP,
    "type": VALID_TYPES,
}

INVALID_MAP = {
    "elements": st.lists(INVALID_UUIDS, min_size=1),
    "removal_point_id": INVALID_UUIDS,
    **EVENT_INVALID_MAP,
    "type": INVALID_TYPES
}


def xfail_construct_remove(elements, removal_point_id, priority, mission_time, type):
    xfail_from_kw(
        RemoveElements, elements=elements, removal_point_id=removal_point_id, priority=priority, mission_time=mission_time, type=type
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(RemoveElements, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "elements": INVALID_MAP["elements"]}
    )
)
def test_invalid_elements(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "removal_point_id": INVALID_MAP["removal_point_id"]}
    )
)
def test_invalid_removal_point_id(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={
            **VALID_MAP,
            "priority": INVALID_MAP["priority"],
        }
    )
)
def test_invalid_priority(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "type": INVALID_MAP["type"]}
    )
)
def test_invalid_type(kw):
    xfail_construct_remove(**kw)
