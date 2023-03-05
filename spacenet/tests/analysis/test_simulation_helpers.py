"""
This module contains tests for helper functions used by the Simulation class.
"""
from typing import List, Optional, Set
from typing_extensions import get_args

import pytest
from hypothesis import given, strategies as st

from spacenet.analysis.simulation import SimElement
from spacenet.analysis.test.utilities import DrawFn
from spacenet.schemas import AllElements

pytestmark = [pytest.mark.analysis, pytest.mark.unit]


def _all_element_contents(
    element: SimElement, visited: Optional[Set[AllElements]] = None
) -> List[SimElement]:
    if visited is None:
        visited = set()
    if element.inner in visited:
        return []
    visited.add(element.inner)
    result = [element] + [
        e
        for contained in element.contents
        for e in _all_element_contents(contained, visited)
    ]
    return result


def _recursive_total_mass(element: SimElement) -> float:
    all_contents = _all_element_contents(element)
    # TODO: fix this test?
    return sum(e.inner.mass for e in all_contents) + element.fuel_mass


all_elements = st.one_of(*(st.builds(ty) for ty in get_args(AllElements)))


recursive_elements = st.recursive(
    base=all_elements.map(lambda e: SimElement(inner=e)),
    extend=lambda children: st.fixed_dictionaries(
        {"inner": all_elements, "contents": st.lists(children, min_size=1)}
    ).map(SimElement.parse_obj),
)


@given(element=recursive_elements)
def test_total_mass(element: SimElement):
    expected_mass = _recursive_total_mass(element)
    actual_mass, _errors = element.total_mass()
    assert expected_mass == pytest.approx(actual_mass)


@st.composite
def multiple_predecessors(draw: DrawFn) -> SimElement:
    """
    Construct a SimElement where one element contained has multiple containers.

    :param draw: function to use for drawing samples; error to provide manually
    :return: uppermost containing element, containing all others
    """
    element = draw(recursive_elements)
    first, second = draw(st.tuples(st.builds(SimElement), st.builds(SimElement)))
    element.contents.append(first)
    element.contents.append(second)
    first.contents.append(second)
    return element


@st.composite
def cyclic_containment(draw: DrawFn) -> SimElement:
    """
    Construct a SimElement where one element contained also contains itself.

    :param draw: function to use for drawing samples; error to provide manually
    :return: the uppermost containing element, containing all others
    """
    element = draw(recursive_elements)
    if not element.contents:
        first, second = draw(st.lists(st.builds(SimElement), min_size=2, max_size=2))
        element.contents.append(first)
        element.contents.append(second)
    element.contents[0].contents.append(element)
    return element


@given(element=multiple_predecessors())
def test_errors_for_multiple_predecessors(element: SimElement):
    _mass, errors = element.total_mass()
    assert errors


@given(element=cyclic_containment())
def test_errors_for_cycle(element: SimElement):
    _mass, errors = element.total_mass()
    assert errors
