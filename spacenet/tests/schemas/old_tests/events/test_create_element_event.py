"""
This module contains tests for CreateElements event schemas.
"""
import pytest
from hypothesis import given, strategies as st

from .spacenet.schemas.element_events import CreateElements
from .utilities import EVENT_VALID_MAP, EVENT_INVALID_MAP
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


VALID_MAP = {
    "elements": st.lists(st.uuids()),
    "container": st.uuids(),
    **EVENT_VALID_MAP,
}

INVALID_MAP = {
    "elements": st.lists(INVALID_UUIDS, min_size=1),
    "container": INVALID_UUIDS,
    **EVENT_INVALID_MAP,
}


def xfail_construct_make(
    name, elements, container, priority, mission_time, type
) -> None:
    """
    Construct a CreateElements event, expecting construction to fail.

    :param name: event name
    :param elements: UUIDs of elements to create
    :param container: UUID of location to create elements at
    :param priority: event priority
    :param mission_time: time event will occur relative to mission start
    :param type: kind of event
    """
    xfail_from_kw(
        CreateElements,
        name=name,
        elements=elements,
        container=container,
        priority=priority,
        mission_time=mission_time,
        type=type,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(CreateElements, **kw)


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "elements": INVALID_MAP["elements"]})
)
def test_invalid_elements(kw):
    xfail_construct_make(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "container": INVALID_MAP["container"]}
    )
)
def test_invalid_container(kw):
    xfail_construct_make(**kw)
