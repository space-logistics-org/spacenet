from heapq import heapify, heappop, heappush
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):

    __slots__ = ["_inner"]

    def __init__(self, initial: Optional[List[T]] = None):
        if initial is None:
            self._inner = []
        else:
            self._inner = initial.copy()
            heapify(self._inner)

    def peek(self) -> Optional[T]:
        if not self._inner:
            return None
        return self._inner[0]

    def push(self, item: T):
        heappush(self._inner, item)

    def pop(self) -> Optional[T]:
        if not self._inner:
            return None
        return heappop(self._inner)

    def __len__(self):
        return len(self._inner)
