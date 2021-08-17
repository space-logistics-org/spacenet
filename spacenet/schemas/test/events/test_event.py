"""
This module contains tests for event schemas.
"""
import pytest
from hypothesis import given, strategies as st

from .utilities import EVENT_VALID_MAP as VALID_MAP, EVENT_INVALID_MAP as INVALID_MAP
from ..utilities import xfail_from_kw, success_from_kw
from spacenet.schemas import Event


pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


def xfail_construct_event(name, priority, mission_time, type) -> None:
    """
    Construct an event, expecting construction to fail.

    :param name: event name
    :param priority: event priority
    :param mission_time: time event will occur relative to mission start
    :param type: kind of event
    """
    xfail_from_kw(Event, name=name, priority=priority, mission_time=mission_time, type=type)


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(Event, **kw)


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "priority": INVALID_MAP["priority"]})
)
def test_invalid_priority(kw):
    xfail_construct_event(**kw)
