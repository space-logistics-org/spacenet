import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import ReconfigureElementsEvent
from .event_utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

STATES = ("Active", "Dormant", "Decommissioned")
VALID_TO_RECONFIGURE = st.dictionaries(keys=st.uuids(), values=st.sampled_from(STATES))
INVALID_TO_RECONFIGURE = st.one_of(
    st.dictionaries(keys=INVALID_UUIDS, values=st.sampled_from(STATES), min_size=1),
    st.dictionaries(
        keys=st.uuids(),
        values=st.text().filter(lambda s: s not in STATES),
        min_size=1,
    ),
    st.dictionaries(
        keys=INVALID_UUIDS,
        values=st.text().filter(lambda s: s not in STATES),
        min_size=1,
    ),
)

VALID_MAP = {
    "to_reconfigure": VALID_TO_RECONFIGURE,
    "reconfigure_point_id": st.uuids(),
}

INVALID_MAP = {
    "to_reconfigure": INVALID_TO_RECONFIGURE,
    "reconfigure_point_id": INVALID_UUIDS,
}


def xfail_construct_reconfigure(
    to_reconfigure, reconfigure_point_id
):
    xfail_from_kw(
        ReconfigureElementsEvent,
        to_reconfigure=to_reconfigure,
        reconfigure_point_id=reconfigure_point_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(ReconfigureElementsEvent, **kw)


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
