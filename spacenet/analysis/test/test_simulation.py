import typing
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pytest
from hypothesis import given, strategies as st

from .utilities import DrawFn
from ..simulation import Simulation
from spacenet.schemas import Scenario


pytestmark = [pytest.mark.analysis]

T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


@st.composite
def listener_builder(
    draw: DrawFn, types: List[Type]
) -> Tuple[SimCallback[T], Optional[T]]:
    ty = draw(st.sampled_from(types))
    ty_strategy = st.from_type(ty)
    v = draw(st.one_of(st.none(), ty_strategy))

    def example_fn(sim: Simulation, prev: Optional[T]):
        pass

    fn = st.functions(like=example_fn, returns=ty_strategy)
    return fn, v


st.register_type_strategy(
    typing.Any, st.one_of(st.integers(), st.text(), st.floats(), st.binary())
)  # placeholder while figuring out where Any annotation is causing problems from


@st.composite
def listener_dict_builder(
    draw: DrawFn, types: List[Type], min_size: int = 0, max_size: Optional[int] = None
) -> Dict[SimCallback[Any], Any]:
    args = draw(st.lists(listener_builder(types), min_size=min_size, max_size=max_size))
    return dict(args)


@given(
    scenario=st.from_type(Scenario),
    pre_listeners=listener_dict_builder(types=[int, float, str]),
    post_listeners=listener_dict_builder(types=[int, float, str]),
)
@pytest.mark.slow
@pytest.mark.xfail
def test_fuzz_simulation(scenario, pre_listeners, post_listeners):
    Simulation(scenario, pre_listeners, post_listeners)
