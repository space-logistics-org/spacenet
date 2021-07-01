import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import ReconfigureElementsEvent
from ..utilities import (
    INVALID_INTS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

VALID_TO_RECONFIGURE = st.dictionaries(keys=st.integers(), values=st.integers())
INVALID_TO_RECONFIGURE = st.one_of(
    st.dictionaries(keys=INVALID_INTS, values=st.integers(), min_size=1),
    st.dictionaries(
        keys=st.integers(),
        values=INVALID_INTS,
        min_size=1,
    ),
    st.dictionaries(
        keys=INVALID_INTS,
        values=INVALID_INTS,
        min_size=1,
    ),
)

VALID_MAP = {
    "to_reconfigure": VALID_TO_RECONFIGURE,
    "reconfigure_point_id": st.integers(),
}

INVALID_MAP = {
    "to_reconfigure": INVALID_TO_RECONFIGURE,
    "reconfigure_point_id": INVALID_INTS,
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
