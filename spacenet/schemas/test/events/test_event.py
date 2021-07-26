import pytest
from hypothesis import given, strategies as st

from .utilities import EVENT_VALID_MAP as VALID_MAP, EVENT_INVALID_MAP as INVALID_MAP
from ..utilities import xfail_from_kw, success_from_kw
from spacenet.schemas import Event


pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


def xfail_construct_event(priority, mission_time):
    return xfail_from_kw(Event, priority=priority, mission_time=mission_time)


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(Event, **kw)


@given(
    kw=st.fixed_dictionaries(mapping={**VALID_MAP, "priority": INVALID_MAP["priority"]})
)
def test_invalid_priority(kw):
    xfail_construct_event(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "mission_time": INVALID_MAP["mission_time"]}
    )
)
def test_invalid_mission_time(kw):
    xfail_construct_event(**kw)
