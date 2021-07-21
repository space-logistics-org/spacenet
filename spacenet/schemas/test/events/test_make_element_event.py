import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import MakeElementsEvent
from ..utilities import (
    INVALID_INTS,
    UNSERIALIZABLE_INTS,
    success_from_kw,
    xfail_from_kw,
)
from spacenet.constants import SQLITE_MAX_INT, SQLITE_MIN_INT

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


VALID_MAP = {
    "element_id": st.lists(
        st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT)
    ),
    "entry_point_id": st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
}

INVALID_MAP = {
    "element_id": st.lists(st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS), min_size=1),
    "entry_point_id": st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS),
}


def xfail_construct_make(element_id, entry_point_id):
    return xfail_from_kw(
        MakeElementsEvent, element_id=element_id, entry_point_id=entry_point_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP),)
def test_valid(kw):
    success_from_kw(MakeElementsEvent, **kw)


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
