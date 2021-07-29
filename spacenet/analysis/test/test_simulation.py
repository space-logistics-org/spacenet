import typing
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import SearchStrategy

from .utilities import DrawFn
from ..simulation import Simulation
from ...analysis.decompose_events import DECOMPOSE_REGISTRY
from spacenet.schemas import Event, PropulsiveBurn, Scenario
from ...schemas.mission import Mission
from ...schemas.space_transport import BurnStageSequence

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

    def example_fn(sim: Simulation, prev: Optional[T]):
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
    pre_listeners=listener_dict_builder(types=[int, float, str]),
    post_listeners=listener_dict_builder(types=[int, float, str]),
)
@pytest.mark.slow
@pytest.mark.xfail
def test_fuzz_simulation(scenario, pre_listeners, post_listeners):
    Simulation(scenario, pre_listeners, post_listeners)


@given(scenario=st.builds(Scenario),)
@pytest.mark.slow
@pytest.mark.xfail
def test_simulation_returns_same(scenario):
    sim = Simulation(scenario)
    sim.run()
    other_sim = Simulation(scenario)
    other_sim.run()
    assert sim.errors == other_sim.errors
    assert sim.result() == other_sim.result()


@given(scenario=st.builds(Scenario),)
@pytest.mark.slow
@pytest.mark.xfail
def test_simulation_empties_queue(scenario):
    sim = Simulation(scenario)
    sim.run()
    assert not sim.event_queue
