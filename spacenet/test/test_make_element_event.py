import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MakeElementEvent
from spacenet.test.event_utilities import (
    INVALID_INTS,
    valid_invalid_from_allowed,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event]

ALLOWED_KINDS = ["Node", "Edge", "ElementCarrier"]
VALID_ELE_IDS = st.integers()
INVALID_ELE_IDS = INVALID_INTS
VALID_KINDS, INVALID_KINDS = valid_invalid_from_allowed(ALLOWED_KINDS)
VALID_ENTRY_IDS = st.integers()
INVALID_ENTRY_IDS = INVALID_ELE_IDS


def xfail_construct_make(element_id, kind, entry_id):
    return xfail_from_kw(
        MakeElementEvent,
        element_id=element_id,
        entry_point_kind=kind,
        entry_point_id=entry_id,
    )


@given(
    ele_id=VALID_ELE_IDS, kind=VALID_KINDS, entry_id=VALID_ENTRY_IDS,
)
def test_valid(ele_id, kind, entry_id):
    event = MakeElementEvent(
        element_id=ele_id, entry_point_kind=kind, entry_point_id=entry_id
    )
    assert event.element_id == ele_id
    assert event.entry_point_kind == kind
    assert event.entry_point_id == entry_id


@given(
    ele_id=INVALID_ELE_IDS, kind=VALID_KINDS, entry_id=VALID_ENTRY_IDS,
)
def test_invalid_element_id(ele_id, kind, entry_id):
    xfail_construct_make(ele_id, kind, entry_id)


@given(
    ele_id=VALID_ELE_IDS, kind=INVALID_KINDS, entry_id=VALID_ENTRY_IDS,
)
def test_invalid_kind(ele_id, kind, entry_id):
    xfail_construct_make(ele_id, kind, entry_id)


@given(
    ele_id=VALID_ELE_IDS, kind=VALID_KINDS, entry_id=INVALID_ENTRY_IDS,
)
def test_invalid_entry_id(ele_id, kind, entry_id):
    xfail_construct_make(ele_id, kind, entry_id)
