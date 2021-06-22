import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import RemoveElementsEvent
from .event_utilities import (
    INVALID_INTS,
    success_from_kw,
    valid_invalid_from_allowed,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event]

ALLOWED_REMOVAL_POINTS = ["Node", "Edge"]
VALID_REMOVALS, INVALID_REMOVALS = valid_invalid_from_allowed(ALLOWED_REMOVAL_POINTS)

VALID_MAP = {
    "to_remove": st.lists(st.integers()),
    "removal_point_kind": VALID_REMOVALS,
    "removal_point_id": st.integers(),
}

INVALID_MAP = {
    "to_remove": st.lists(INVALID_INTS, min_size=1),
    "removal_point_kind": INVALID_REMOVALS,
    "removal_point_id": INVALID_INTS,
}


def xfail_construct_remove(to_remove, removal_point_kind, removal_point_id):
    xfail_from_kw(
        RemoveElementsEvent,
        to_remove=to_remove,
        removal_point_kind=removal_point_kind,
        removal_point_id=removal_point_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(RemoveElementsEvent, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "to_remove": INVALID_MAP["to_remove"]}
    )
)
def test_invalid_to_remove(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "removal_point_kind": INVALID_MAP["removal_point_kind"]}
    )
)
def test_invalid_removal_point_kind(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "removal_point_id": INVALID_MAP["removal_point_id"]}
    )
)
def test_invalid_removal_point_id(kw):
    xfail_construct_remove(**kw)
