"""
This module contains tests for MakeElements event schemas.
"""
import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MakeElements
from .utilities import EVENT_VALID_MAP, EVENT_INVALID_MAP
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


VALID_MAP = {
    "elements": st.lists(st.uuids()),
    "entry_point_id": st.uuids(),
    **EVENT_VALID_MAP,
}

INVALID_MAP = {
    "elements": st.lists(INVALID_UUIDS, min_size=1),
    "entry_point_id": INVALID_UUIDS,
    **EVENT_INVALID_MAP,
}


def xfail_construct_make(
    elements, entry_point_id, priority, mission_time, type
) -> None:
    """
    Construct a MakeElements event, expecting construction to fail.

    :param elements: UUIDs of elements to create
    :param entry_point_id: UUID of location to create elements at
    :param priority: event priority
    :param mission_time: time event will occur relative to mission start
    :param type: kind of event
    """
    xfail_from_kw(
        MakeElements,
        elements=elements,
        entry_point_id=entry_point_id,
        priority=priority,
        mission_time=mission_time,
        type=type,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(MakeElements, **kw)


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "elements": INVALID_MAP["elements"]})
)
def test_invalid_elements(kw):
    xfail_construct_make(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "entry_point_id": INVALID_MAP["entry_point_id"]}
    )
)
def test_invalid_entry_point_id(kw):
    xfail_construct_make(**kw)
