import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MoveElements
from .utilities import EVENT_INVALID_MAP, EVENT_VALID_MAP, VALID_PRIORITIES, INVALID_PRIORITIES
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_MAP = {
    "to_move": st.lists(
        st.uuids()
    ),
    "origin_id": st.uuids(),
    "destination_id": st.uuids(),
    **EVENT_VALID_MAP
}

INVALID_MAP = {
    "to_move": st.lists(INVALID_UUIDS, min_size=1),
    "origin_id": INVALID_UUIDS,
    "destination_id": INVALID_UUIDS,
    **EVENT_INVALID_MAP
}


def xfail_construct_move(to_move, origin_id, destination_id, priority, mission_time):
    xfail_from_kw(
        MoveElements,
        to_move=to_move,
        origin_id=origin_id,
        destination_id=destination_id,
        priority=priority,
        mission_time=mission_time
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(
        MoveElements, **kw,
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

@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "priority": INVALID_MAP["priority"]}
    )
)
def test_invalid_priority(kw):
    xfail_construct_move(**kw)
