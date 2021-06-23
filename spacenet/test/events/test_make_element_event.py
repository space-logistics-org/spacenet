import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MakeElementEvent
from .event_utilities import (
    INVALID_INTS,
    valid_invalid_from_allowed,
    xfail_from_kw,
    success_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

ALLOWED_KINDS = ["Node", "Edge", "ElementCarrier"]
VALID_ELE_IDS = st.integers()
INVALID_ELE_IDS = INVALID_INTS
VALID_KINDS, INVALID_KINDS = valid_invalid_from_allowed(ALLOWED_KINDS)
VALID_ENTRY_IDS = st.integers()
INVALID_ENTRY_IDS = INVALID_ELE_IDS


VALID_MAP = {
    "element_id": st.integers(),
    "entry_point_kind": VALID_KINDS,
    "entry_point_id": st.integers(),
}

INVALID_MAP = {
    "element_id": INVALID_INTS,
    "entry_point_kind": INVALID_KINDS,
    "entry_point_id": INVALID_INTS,
}


def xfail_construct_make(element_id, entry_point_kind, entry_point_id):
    return xfail_from_kw(
        MakeElementEvent,
        element_id=element_id,
        entry_point_kind=entry_point_kind,
        entry_point_id=entry_point_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(MakeElementEvent, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "element_id": INVALID_MAP["element_id"]}
    )
)
def test_invalid_element_id(kw):
    xfail_construct_make(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "entry_point_kind": INVALID_MAP["entry_point_kind"]}
    )
)
def test_invalid_entry_point_kind(kw):
    xfail_construct_make(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "entry_point_id": INVALID_MAP["entry_point_id"]}
    )
)
def test_invalid_entry_point_id(kw):
    xfail_construct_make(**kw)
