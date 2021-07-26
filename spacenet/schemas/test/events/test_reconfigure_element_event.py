import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import ReconfigureElements
from .utilities import EVENT_VALID_MAP, INVALID_PRIORITIES, VALID_PRIORITIES
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_TO_RECONFIGURE = st.dictionaries(
    keys=st.uuids(),
    values=st.uuids(),
)
INVALID_TO_RECONFIGURE = st.one_of(
    st.dictionaries(
        keys=INVALID_UUIDS,
        values=st.uuids(),
        min_size=1,
    ),
    st.dictionaries(
        keys=st.integers(),
        values=INVALID_UUIDS,
        min_size=1,
    ),
    st.dictionaries(
        keys=INVALID_UUIDS,
        values=INVALID_UUIDS,
        min_size=1,
    ),
)

VALID_MAP = {
    "to_reconfigure": VALID_TO_RECONFIGURE,
    "reconfigure_point_id": st.uuids(),
    **EVENT_VALID_MAP
}

INVALID_MAP = {
    "to_reconfigure": INVALID_TO_RECONFIGURE,
    "reconfigure_point_id": INVALID_UUIDS,
    "priority": INVALID_PRIORITIES
}


def xfail_construct_reconfigure(to_reconfigure, reconfigure_point_id, priority, mission_time):
    xfail_from_kw(
        ReconfigureElements,
        to_reconfigure=to_reconfigure,
        reconfigure_point_id=reconfigure_point_id,
        priority=priority,
        mission_time=mission_time
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(ReconfigureElements, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "to_reconfigure": INVALID_MAP["to_reconfigure"]}
    )
)
def test_invalid_to_reconfigure(kw):
    xfail_construct_reconfigure(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={
            **VALID_MAP,
            "reconfigure_point_id": INVALID_MAP["reconfigure_point_id"],
        }
    )
)
def test_invalid_reconfigure_point_id(kw):
    xfail_construct_reconfigure(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={
            **VALID_MAP,
            "priority": INVALID_MAP["priority"],
        }
    )
)
def test_invalid_priority(kw):
    xfail_construct_reconfigure(**kw)
