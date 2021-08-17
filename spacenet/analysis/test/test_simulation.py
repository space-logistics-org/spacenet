"""
This module contains tests for the Simulation class' ``run`` method, ensuring that some basic
properties of running a simulation are upheld.
"""
import typing
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar

import pytest
from hypothesis import assume, given, strategies as st

from .utilities import DrawFn, build_checked_scenario
from ..exceptions import SimException
from ..simulation import Simulation

pytestmark = [pytest.mark.analysis, pytest.mark.unit]

T = TypeVar("T")
SimCallback = Callable[["Simulation", Optional[T]], T]


# TODO: we need a better Network builder. Maybe use hypothesis-networkx for performance.


@st.composite
def listener_builder(
    draw: DrawFn, types: List[Type]
) -> Tuple[SimCallback[T], Optional[T]]:
    """
    Construct a listener callback and its initial input.

    :param draw: function to use for drawing samples; error to provide manually
    :param types: types of listeners to create
    :return: tuple of functions and initial inputs to those functions
    """
    ty = draw(st.sampled_from(types))
    ty_strategy = st.from_type(ty)
    v = draw(st.one_of(st.none(), ty_strategy))

    # noinspection PyMissingOrEmptyDocstring
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
    """
    Construct a dictionary of listener callbacks.

    :param draw: function to use for drawing samples; error to provide manually
    :param types: types of listeners to create
    :param min_size: minimum listener dictionary size
    :param max_size: maximum listener dictionary size
    :return: dictionary of listener functions mapped to their initial values
    """
    args = draw(st.lists(listener_builder(types), min_size=min_size, max_size=max_size))
    return dict(args)


@given(
    scenario=build_checked_scenario,
    propulsive=st.booleans(),
    pre_listeners=listener_dict_builder(types=[int, float, str]),
    post_listeners=listener_dict_builder(types=[int, float, str]),
)
@pytest.mark.slow
def test_fuzz_simulation(scenario, propulsive, pre_listeners, post_listeners):
    try:
        sim = Simulation(scenario, pre_listeners, post_listeners, propulsive=propulsive)
    except SimException:
        assume(False)
        return
    sim.run()


@given(
    scenario=build_checked_scenario,
    propulsive=st.booleans(),
)
@pytest.mark.slow
def test_simulation_returns_same(scenario, propulsive):
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except SimException:
        assume(False)
        return
    sim.run()
    other_sim = Simulation(scenario, propulsive=propulsive)
    other_sim.run()
    assert sim.errors == other_sim.errors
    assert sim.result == other_sim.result


@given(
    scenario=build_checked_scenario,
    propulsive=st.booleans(),
)
@pytest.mark.slow
def test_simulation_empties_queue(scenario, propulsive):
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except SimException:
        assume(False)
        return
    sim.run()
    assert not sim.event_queue


# TODO: another property is that all MoveElements events end up with their constituent
#  elements ending up at their final destinations by the end, regardless of errors, unless
#  removed

# TODO: would like to have a way to construct Scenarios matching some constraints, sort of
#  as partitions
