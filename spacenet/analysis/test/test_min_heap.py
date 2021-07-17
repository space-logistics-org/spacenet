from heapq import heapify, heappop, heappush

import pytest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule

from spacenet.analysis.min_heap import MinHeap

pytestmark = [pytest.mark.analysis]


class HeapModel(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = []
        self.heap = MinHeap()

    @rule(xs=st.lists(st.integers()))
    def init_from_existing(self, xs):
        self.model = xs
        heapify(self.model)
        self.heap = MinHeap(xs)

    @rule(item=st.integers())
    def push(self, item):
        heappush(self.model, item)
        self.heap.push(item)

    @rule()
    def pop(self):
        if not self.model:
            assert 0 == len(self.heap)
            assert not self.heap
            return
        item = heappop(self.model)
        assert item == self.heap.pop()

    @rule()
    def same_len(self):
        assert len(self.model) == len(self.heap)

    @rule()
    def peek(self):
        if not self.model:
            assert 0 == len(self.heap)
            assert not self.heap
            return
        item = self.model[0]
        assert item == self.heap.peek()


TestMinHeap = HeapModel.TestCase
