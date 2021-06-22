import pytest
from hypothesis import given, strategies as st
from pydantic import ValidationError

from spacenet.schemas.element_events import MakeElementEvent

pytestmark = [pytest.mark.unit, pytest.mark.event]

ALLOWED_KINDS = ["Node", "Edge", "ElementCarrier"]
VALID_ELE_IDS = st.integers()
INVALID_ELE_IDS = st.one_of(
    st.integers().map(lambda x: x + 0.1),
    st.text().filter(lambda s: not is_integer(s)))
VALID_KINDS = st.sampled_from(ALLOWED_KINDS)
INVALID_KINDS = st.text().filter(lambda s: s not in ALLOWED_KINDS)
VALID_ENTRY_IDS = st.integers()
INVALID_ENTRY_IDS = INVALID_ELE_IDS


@given(
    ele_id=VALID_ELE_IDS,
    kind=VALID_KINDS,
    entry_id=VALID_ENTRY_IDS,
)
def test_valid_constructions(ele_id, kind, entry_id):
    event = MakeElementEvent(
        element_id=ele_id, entry_point_kind=kind, entry_point_id=entry_id
    )
    assert event.element_id == ele_id
    assert event.entry_point_kind.value == kind
    assert event.entry_point_id == entry_id


def is_integer(s: str) -> bool:
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def xfail_construct(ele_id, kind, entry_id) -> None:
    try:
        MakeElementEvent(
            element_id=ele_id, entry_point_kind=kind, entry_point_id=entry_id
        )
    except ValidationError:
        pass
    else:
        assert False, "shouldn't get here"


@given(
    ele_id=INVALID_ELE_IDS,
    kind=VALID_KINDS,
    entry_id=VALID_ENTRY_IDS,
)
def test_invalid_element_id(ele_id, kind, entry_id):
    xfail_construct(ele_id, kind, entry_id)


@given(
    ele_id=VALID_ELE_IDS,
    kind=INVALID_KINDS,
    entry_id=VALID_ENTRY_IDS,
)
def test_invalid_kind(ele_id, kind, entry_id):
    xfail_construct(ele_id, kind, entry_id)


@given(
    ele_id=VALID_ELE_IDS,
    kind=VALID_KINDS,
    entry_id=INVALID_ENTRY_IDS,
)
def test_invalid_entry_id(ele_id, kind, entry_id):
    xfail_construct(ele_id, kind, entry_id)
