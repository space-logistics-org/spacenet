from hypothesis import strategies as st
__all__ = [
    "VALID_PRIORITIES", "INVALID_PRIORITIES"
]
VALID_PRIORITIES = st.integers(min_value=1, max_value=5)
INVALID_PRIORITIES = st.one_of(st.integers(max_value=0), st.integers(min_value=6))
