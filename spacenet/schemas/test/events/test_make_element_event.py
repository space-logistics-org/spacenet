import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MakeElements
from .utilities import INVALID_PRIORITIES, VALID_PRIORITIES
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


VALID_MAP = {
    "element_id": st.lists(
        st.uuids()
    ),
    "entry_point_id": st.uuids(),
    "priority": VALID_PRIORITIES
}

INVALID_MAP = {
    "element_id": st.lists(INVALID_UUIDS, min_size=1),
    "entry_point_id": INVALID_UUIDS,
    "priority": INVALID_PRIORITIES,
}


def xfail_construct_make(element_id, entry_point_id, priority):
    return xfail_from_kw(
        MakeElements, element_id=element_id, entry_point_id=entry_point_id, priority=priority
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(MakeElements, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "element_id": INVALID_MAP["element_id"]}
    )
)
def test_invalid_element_ids(kw):
    xfail_construct_make(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "entry_point_id": INVALID_MAP["entry_point_id"]}
    )
)
def test_invalid_entry_point_id(kw):
    xfail_construct_make(**kw)
