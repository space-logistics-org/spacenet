from hypothesis import strategies as st
from typing import Callable, TypeVar

T = TypeVar("T")
DrawFn = Callable[[st.SearchStrategy[T]], T]
