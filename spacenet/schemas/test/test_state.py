import pytest
from hypothesis import given, strategies as st
from .utilities import INVALID_INTS, success_from_kw, xfail_from_kw
from spacenet.schemas.constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from ..state import State

pytestmark = [pytest.mark.unit, pytest.mark.state, pytest.mark.schema]

LEGAL_STATES = ("Active", "Quiescent", "Dormant", "Decommissioned")
BOOL_STRINGS = ("0", "off", "f", "false", "n", "no", "1", "on", "t", "true", "y", "yes")
BOOL_ALTS = (
    (0, 1) + BOOL_STRINGS + tuple(map(lambda s: bytes(s, "utf-8"), BOOL_STRINGS))
)

VALID_MAP = {
    "element_id": st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
    "name": st.text(),
    "state_type": st.sampled_from(LEGAL_STATES),
    "is_initial_state": st.booleans(),
}

INVALID_MAP = {
    "element_id": st.one_of(
        INVALID_INTS,
        st.integers(max_value=SQLITE_MIN_INT - 1),
        st.integers(min_value=SQLITE_MAX_INT + 1),
    ),
    "state_type": st.text().filter(lambda s: s not in LEGAL_STATES),
    "is_initial_state": st.one_of(st.text(), st.sampled_from(BOOL_ALTS)),
}


def xfail_construct_state(element_id, name, state_type, is_initial_state):
    xfail_from_kw(
        State,
        element_id=element_id,
        name=name,
        state_type=state_type,
        is_initial_state=is_initial_state,
    )


@given(kw=st.fixed_dictionaries(VALID_MAP))
def test_valid(kw):
    success_from_kw(State, **kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "element_id": INVALID_MAP["element_id"]}
    )
)
def test_invalid_element_id(kw):
    xfail_construct_state(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "state_type": INVALID_MAP["state_type"]}
    )
)
def test_invalid_state_type(kw):
    xfail_construct_state(**kw)


@given(
    kw=st.fixed_dictionaries(
        mapping={**VALID_MAP, "is_initial_state": INVALID_MAP["is_initial_state"]}
    )
)
def test_invalid_initial_state(kw):
    xfail_construct_state(**kw)
