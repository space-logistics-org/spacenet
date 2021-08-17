"""
This module contains tests for the MinHeap implementation provided, ensuring that it works
the same way as the procedural methods provided in the heapq module.
"""
from heapq import heapify, heappop, heappush
from itertools import tee
from typing import Iterable, List, Tuple, TypeVar

import pytest
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from .utilities import DrawFn
from spacenet.analysis.min_heap import MinHeap

pytestmark = [pytest.mark.analysis, pytest.mark.unit]


def check_heap_invariant(heap: MinHeap) -> None:
    """
    Verify that the heap invariant holds for the provided MinHeap.

    :param heap: heap to verify heap invariant of
    :raises AssertionError: if heap invariant does not hold
    """
    n = len(heap)
    for i in range(n):
        if 2 * i + 1 < n:
            assert heap[i] <= heap[2 * i + 1]
        if 2 * i + 2 < n:
            assert heap[i] <= heap[2 * i + 2]


class HeapModel(RuleBasedStateMachine):
    """
    A class defining a stateful test for MinHeap.
    """
    def __init__(self):
        super().__init__()
        self.model = []
        self.heap = MinHeap()

    @rule(xs=st.lists(st.integers()))
    def _init_from_existing(self, xs):
        self.model = xs
        heapify(self.model)
        self.heap = MinHeap(xs)

    @rule(item=st.integers())
    def _push(self, item):
        heappush(self.model, item)
        self.heap.push(item)

    @rule()
    def _pop(self):
        if not self.model:
            assert 0 == len(self.heap)
            assert not self.heap
            return
        item = heappop(self.model)
        assert item == self.heap.pop()

    @invariant()
    def _same_len(self):
        assert len(self.model) == len(self.heap)

    @invariant()
    def _heap_invariant(self):
        check_heap_invariant(self.heap)

    @invariant()
    def _correct_min(self):
        if not self.model:
            assert 0 == len(self.heap)
            assert not self.heap
            return
        item = self.model[0]
        assert item == self.heap.peek() == self.heap[0]

    @invariant()
    def _iter_contains_all(self):
        assert set(self.model) == set(self.heap)


TestMinHeapStateful = HeapModel.TestCase

T = TypeVar("T")


@st.composite
def iterable_and_list(
    draw: DrawFn, elements: st.SearchStrategy[T]
) -> Tuple[Iterable[T], List[T]]:
    """
    Provide an iterable and list over the same elements, drawn from ``elements``, in the same
    order.

    :param draw: function to use for drawing samples; error to provide manually
    :param elements: elements of iterable / list
    :return: iterable and list over the same elements in the same order
    """
    xs = draw(st.iterables(elements))
    xs, xs_cpy = tee(xs)
    xs_cpy = list(xs_cpy)
    return xs, xs_cpy


@given(xs_and_copy=iterable_and_list(st.integers()))
def test_min_heap(xs_and_copy):
    xs, xs_cpy = xs_and_copy
    from_init = MinHeap(xs)
    check_heap_invariant(from_init)
    via_push = MinHeap()
    for n in xs_cpy:
        via_push.push(n)
    check_heap_invariant(via_push)
    assert from_init.peek() == via_push.peek()
    if not xs_cpy:
        with pytest.raises(IndexError):
            _should_fail = from_init[0]
        with pytest.raises(IndexError):
            _should_fail = via_push[0]
        assert from_init.peek() is None
        assert via_push.peek() is None


@given(
    xs_and_copy=st.one_of(
        *(
            iterable_and_list(t)
            for t in (st.integers(), st.floats(allow_nan=False), st.text())
        )
    )
)
def test_infallible_push(xs_and_copy):
    xs, xs_cpy = xs_and_copy
    heap = MinHeap()
    for n in xs:
        heap.push(n)
    if xs_cpy:
        assert min(xs_cpy) == heap.peek()
