import pytest

from hypothesis import given, strategies as st

pytestmark = [pytest.mark.unit, pytest.mark.event]


@given(
    ele_id=st.integers(),
    kind=st.sampled_from(("Node", "Edge", "EdgeCarrier")),
    entry_id=st.integers(),
)
def test_valid_constructions(ele_id, kind, entry_id):
    pass
