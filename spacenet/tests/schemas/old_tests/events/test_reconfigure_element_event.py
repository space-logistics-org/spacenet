"""
This module contains tests for ReconfigureElements event schemas.
"""
import pytest
from hypothesis import given, strategies as st

from .spacenet.schemas.element_events import ReconfigureElements
from .utilities import EVENT_VALID_MAP, INVALID_PRIORITIES
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_element_states = st.dictionaries(keys=st.uuids(), values=int,)
INVALID_element_states = st.one_of(
    st.dictionaries(keys=INVALID_UUIDS, values=st.uuids(), min_size=1,),
    st.dictionaries(keys=st.integers(), values=INVALID_UUIDS, min_size=1,),
    st.dictionaries(keys=INVALID_UUIDS, values=INVALID_UUIDS, min_size=1,),
)

VALID_MAP = {
    "element_states": VALID_element_states,
    "location": st.uuids(),
    **EVENT_VALID_MAP,
}

INVALID_MAP = {
    "element_states": INVALID_element_states,
    "location": INVALID_UUIDS,
    "priority": INVALID_PRIORITIES,
}


def xfail_construct_reconfigure(
    name, element_states, location, priority, mission_time, type
):
    """
    Construct a ReconfigureElements event, expecting construction to fail.

    :param name: event name
    :param element_states: UUIDs of elements to reconfigure
    :param location: UUID of location to reconfigure elements at
    :param priority: event priority
    :param mission_time: time event will occur relative to mission start
    :param type: kind of event
    """
    xfail_from_kw(
        ReconfigureElements,
        name=name,
        element_states=element_states,
        location=location,
        priority=priority,
        mission_time=mission_time,
        type=type,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(ReconfigureElements, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "element_states": INVALID_MAP["element_states"]}
    )
)
def test_invalid_element_states(kw):
    xfail_construct_reconfigure(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={
            **VALID_MAP,
            "location": INVALID_MAP["location"],
        }
    )
)
def test_invalid_location(kw):
    xfail_construct_reconfigure(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "priority": INVALID_MAP["priority"],}
    )
)
def test_invalid_priority(kw):
    xfail_construct_reconfigure(**kw)
