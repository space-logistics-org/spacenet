import typing
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pytest
from hypothesis import assume, given, strategies as st

from .utilities import DrawFn
from ..simulation import Simulation
from spacenet.schemas import Scenario

pytestmark = [pytest.mark.analysis, pytest.mark.unit]

T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


@st.composite
def listener_builder(
        draw: DrawFn, types: List[Type]
) -> Tuple[SimCallback[T], Optional[T]]:
    ty = draw(st.sampled_from(types))
    ty_strategy = st.from_type(ty)
    v = draw(st.one_of(st.none(), ty_strategy))

    def example_fn(_sim: Simulation, _prev: Optional[T]):
        pass

    fn = draw(st.functions(like=example_fn, returns=ty_strategy))
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
    scenario=st.builds(Scenario),
    propulsive=st.booleans(),
    pre_listeners=listener_dict_builder(types=[int, float, str]),
    post_listeners=listener_dict_builder(types=[int, float, str]),
)
@pytest.mark.slow
@pytest.mark.xfail
def test_fuzz_simulation(scenario, propulsive, pre_listeners, post_listeners):
    Simulation(scenario, pre_listeners, post_listeners, propulsive=propulsive)


@given(scenario=st.builds(Scenario), propulsive=st.booleans(),)
@pytest.mark.slow
@pytest.mark.xfail
def test_simulation_returns_same(scenario, propulsive):
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except ValueError:
        assume(False)
        return
    sim.run()
    other_sim = Simulation(scenario, propulsive=propulsive)
    other_sim.run()
    assert sim.errors == other_sim.errors
    assert sim.result() == other_sim.result()


@given(scenario=st.builds(Scenario), propulsive=st.booleans(),)
@pytest.mark.slow
@pytest.mark.xfail
def test_simulation_empties_queue(scenario, propulsive):
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except ValueError:
        assume(False)
        return
    sim.run()
    assert not sim.event_queue

# TODO: another property is that all MoveElements events end up with their constituent
#  elements ending up at their final destinations by the end, regardless of errors

# TODO: would like to have a way to construct Scenarios matching some constraints, sort of
#  as partitions
