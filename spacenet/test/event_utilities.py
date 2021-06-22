from typing import List, Tuple

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy
from pydantic import ValidationError


def is_integer(s: str) -> bool:
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


INVALID_INTS = st.one_of(
    st.integers().map(lambda x: x + 0.1), st.text().filter(lambda s: not is_integer(s))
)


def valid_invalid_from_allowed(
    allowed: List[str],
) -> Tuple[SearchStrategy, SearchStrategy]:
    valid = st.sampled_from(allowed)
    invalid = st.text().filter(lambda s: s not in allowed)
    return valid, invalid


def success_from_kw(type_, **kwargs) -> None:
    event = type_.parse_obj(kwargs)
    for name, val in kwargs.items():
        assert val == getattr(event, name)


def xfail_from_kw(type_, **kwargs) -> None:
    try:
        type_.parse_obj(kwargs)
    except ValidationError:
        return
    else:
        assert False, f"Expected construction of {type_.__name__} with {kwargs} to fail"
