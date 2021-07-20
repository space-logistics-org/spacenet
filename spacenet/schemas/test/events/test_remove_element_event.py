import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import RemoveElementsEvent
from ..utilities import (
    INVALID_INTS,
    UNSERIALIZABLE_INTS,
    success_from_kw,
    valid_invalid_from_allowed,
    xfail_from_kw,
)
from spacenet.constants import SQLITE_MAX_INT, SQLITE_MIN_INT

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

ALLOWED_REMOVAL_POINTS = ["Node", "Edge"]
VALID_REMOVALS, INVALID_REMOVALS = valid_invalid_from_allowed(ALLOWED_REMOVAL_POINTS)

VALID_MAP = {
    "to_remove": st.lists(
        st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT)
    ),
    "removal_point_id": st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
}

INVALID_MAP = {
    "to_remove": st.lists(st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS), min_size=1),
    "removal_point_id": st.one_of(INVALID_INTS, UNSERIALIZABLE_INTS),
}


def xfail_construct_remove(to_remove, removal_point_id):
    xfail_from_kw(
        RemoveElementsEvent, to_remove=to_remove, removal_point_id=removal_point_id,
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(RemoveElementsEvent, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "to_remove": INVALID_MAP["to_remove"]}
    )
)
def test_invalid_to_remove(kw):
    xfail_construct_remove(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "removal_point_id": INVALID_MAP["removal_point_id"]}
    )
)
def test_invalid_removal_point_id(kw):
    xfail_construct_remove(**kw)
