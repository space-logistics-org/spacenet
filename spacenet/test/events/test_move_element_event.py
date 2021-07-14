import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MoveElementsEvent
from ..utilities import (
    INVALID_INTS,
    UNSERIALIZABLE_INTS,
    success_from_kw,
    xfail_from_kw,
)
from ...constants import SQLITE_MAX_INT, SQLITE_MIN_INT

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_MAP = {
    "to_move": st.lists(
        st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT)
    ),
    "origin_id": st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
    "destination_id": st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
}

INVALID_MAP = {
    "to_move": st.lists(st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS), min_size=1),
    "origin_id": st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS),
    "destination_id": st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS),
}


def xfail_construct_move(to_move, origin_id, destination_id):
    xfail_from_kw(
        MoveElementsEvent,
        to_move=to_move,
        origin_id=origin_id,
        destination_id=destination_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(
        MoveElementsEvent, **kw,
    )


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "to_move": INVALID_MAP["to_move"]})
)
def test_invalid_to_move(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "origin_id": INVALID_MAP["origin_id"]}
    )
)
def test_invalid_origin_id(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "destination_id": INVALID_MAP["destination_id"]}
    )
)
def test_invalid_destination_id(kw):
    xfail_construct_move(**kw)
