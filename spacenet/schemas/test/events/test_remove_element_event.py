import pytest
from hypothesis import given, strategies as st

from spacenet.schemas.element_events import RemoveElements
from .utilities import INVALID_PRIORITIES, VALID_PRIORITIES
from ..utilities import (
    INVALID_UUIDS,
    success_from_kw,
    valid_invalid_from_allowed,
    xfail_from_kw,
)

pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]

ALLOWED_REMOVAL_POINTS = ["Node", "Edge"]
VALID_REMOVALS, INVALID_REMOVALS = valid_invalid_from_allowed(ALLOWED_REMOVAL_POINTS)

VALID_MAP = {
    "to_remove": st.lists(
        st.uuids()
    ),
    "removal_point_id": st.uuids(),
    "priority": VALID_PRIORITIES,
}

INVALID_MAP = {
    "to_remove": st.lists(INVALID_UUIDS, min_size=1),
    "removal_point_id": INVALID_UUIDS,
    "priority": INVALID_PRIORITIES
}


def xfail_construct_remove(to_remove, removal_point_id, priority):
    xfail_from_kw(
        RemoveElements, to_remove=to_remove, removal_point_id=removal_point_id, priority=priority
    )


@given(kw=st.fixed_dictionaries(mapping=VALID_MAP))
def test_valid(kw):
    success_from_kw(RemoveElements, **kw)


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


@given(
    kw=st.fixed_dictionaries(
        mapping={
            **VALID_MAP,
            "priority": INVALID_MAP["priority"],
        }
    )
)
def test_invalid_priority(kw):
    xfail_construct_remove(**kw)
