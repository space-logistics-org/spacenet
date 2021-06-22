import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MoveElementsEvent
from spacenet.test.event_utilities import (
    INVALID_INTS,
    valid_invalid_from_allowed,
    xfail_from_kw,
    success_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event]

ALLOWED_ORIGINS = ["Node", "Edge"]
ALLOWED_DESTINATIONS = ["Node", "Edge", "ElementCarrier"]
VALID_ORIGINS, INVALID_ORIGINS = valid_invalid_from_allowed(ALLOWED_ORIGINS)
VALID_DESTS, INVALID_DESTS = valid_invalid_from_allowed(ALLOWED_DESTINATIONS)

VALID_MAP = {
    "to_move": st.lists(st.integers()),
    "origin_id": st.integers(),
    "destination_id": st.integers(),
    "origin_kind": VALID_ORIGINS,
    "destination_kind": VALID_DESTS,
}

INVALID_MAP = {
    "to_move": st.lists(INVALID_INTS, min_size=1),
    "origin_id": INVALID_INTS,
    "destination_id": INVALID_INTS,
    "origin_kind": INVALID_ORIGINS,
    "destination_kind": INVALID_DESTS,
}


def xfail_construct_move(
    to_move, origin_kind, origin_id, destination_kind, destination_id
):
    xfail_from_kw(
        MoveElementsEvent,
        to_move=to_move,
        origin_kind=origin_kind,
        origin_id=origin_id,
        destination_kind=destination_kind,
        destination_id=destination_id,
    )


@given(
    kw=st.fixed_dictionaries(mapping=VALID_MAP)
)
def test_valid(kw):
    success_from_kw(
        MoveElementsEvent,
        **kw,
    )


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "to_move": INVALID_MAP["to_move"]})
)
def test_invalid_to_move(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "origin_kind": INVALID_MAP["origin_kind"]}
    )
)
def test_invalid_origin_kind(kw):
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
        mapping={**VALID_MAP, "destination_kind": INVALID_MAP["destination_kind"]}
    )
)
def test_invalid_destination_kind(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "destination_id": INVALID_MAP["destination_id"]}
    )
)
def test_invalid_destination_id(kw):
    xfail_construct_move(**kw)
