from typing import List, Optional, Set

import pytest
from hypothesis import given, strategies as st

from spacenet.analysis.simulation import SimElement

pytestmark = [pytest.mark.analysis, pytest.mark.unit]


def _all_element_contents(
    element: SimElement, visited: Optional[Set[SimElement]] = None
) -> List[SimElement]:
    if visited is None:
        visited = set()  # fixme: this is a performance problem
    if element in visited:
        return []
    visited.add(element)
    result = [element] + [
        e
        for contained in element.contents
        for e in _all_element_contents(contained, visited)
    ]
    return result


def _recursive_total_mass(element: SimElement) -> float:
    all_contents = _all_element_contents(element)
    return sum(e.inner.mass for e in all_contents)


# TODO: write a recursive strategy to make these


@given(element=st.builds(SimElement))
def test_total_mass(element: SimElement):
    expected_mass = _recursive_total_mass(element)
    actual_mass, _errors = element.total_mass()
    assert expected_mass == actual_mass
