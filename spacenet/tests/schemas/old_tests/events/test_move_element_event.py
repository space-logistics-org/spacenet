"""
This module contains tests for MoveElements event schemas.
"""
import pytest
from hypothesis import given, strategies as st

from .spacenet.schemas.element_events import MoveElements
from .utilities import (
    EVENT_INVALID_MAP,
    EVENT_VALID_MAP,
)
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_MAP = {
    "elements": st.lists(st.uuids()),
    "location": st.uuids(),
    "container": st.uuids(),
    **EVENT_VALID_MAP,
}

INVALID_MAP = {
    "elements": st.lists(INVALID_UUIDS, min_size=1),
    "location": INVALID_UUIDS,
    "container": INVALID_UUIDS,
    **EVENT_INVALID_MAP,
}


def xfail_construct_move(
    name, elements, location, container, priority, mission_time, type
) -> None:
    """
    Construct a MoveElements event, expecting construction to fail.

    :param name: event name
    :param elements: UUIDs of elements to move
    :param location: UUID of starting location of elements
    :param container: UUID of destination of elements
    :param priority: event priority
    :param mission_time: time event will occur relative to mission start
    :param type: kind of event
    """

    xfail_from_kw(
        MoveElements,
        name=name,
        elements=elements,
        location=location,
        container=container,
        priority=priority,
        mission_time=mission_time,
        type=type,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(
        MoveElements, **kw,
    )


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "elements": INVALID_MAP["elements"]})
)
def test_invalid_elements(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "location": INVALID_MAP["location"]}
    )
)
def test_invalid_location(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "container": INVALID_MAP["container"]}
    )
)
def test_invalid_container(kw):
    xfail_construct_move(**kw)


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "priority": INVALID_MAP["priority"]})
)
def test_invalid_priority(kw):
    xfail_construct_move(**kw)
