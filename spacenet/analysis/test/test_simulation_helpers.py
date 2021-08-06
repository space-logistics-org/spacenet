from typing import List, Optional, Set
from typing_extensions import get_args

import pytest
from hypothesis import given, infer, strategies as st

from spacenet.analysis.simulation import SimElement
from spacenet.schemas import AllElements

pytestmark = [pytest.mark.analysis, pytest.mark.unit]


def _all_element_contents(
    element: SimElement, visited: Optional[Set[SimElement]] = None
) -> List[SimElement]:
    if visited is None:
        visited = set()
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


all_elements = st.one_of(*(st.builds(ty) for ty in get_args(AllElements)))


recursive_elements = st.recursive(
    base=all_elements.map(lambda e: SimElement(inner=e)),
    extend=lambda children: st.fixed_dictionaries(
        {"inner": all_elements, "contents": st.lists(children)}
    ).map(SimElement.parse_obj),
)


st.register_type_strategy(SimElement, recursive_elements)


@given(element=infer)
def test_total_mass(element: SimElement):
    expected_mass = _recursive_total_mass(element)
    actual_mass, _errors = element.total_mass()
    assert expected_mass == pytest.approx(actual_mass)
