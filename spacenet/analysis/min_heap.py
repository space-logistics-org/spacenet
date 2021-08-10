from heapq import heapify, heappop, heappush
from typing import Generator, Generic, Iterable, Optional, TypeVar

T = TypeVar("T")


class MinHeap(Generic[T]):
    """
    A wrapper around the procedural methods provided in the heapq library. Provides a minimal
    priority queue implementation via an array-backed binary heap.
    """

    __slots__ = ["_inner"]

    def __init__(self, initial: Optional[Iterable[T]] = None):
        if initial is None:
            self._inner = []
        else:
            self._inner = list(initial)
            heapify(self._inner)

    def peek(self) -> Optional[T]:
        """
        View a smallest item on the heap, or return None if no items are present.

        :return: a smallest element in the heap, or None if no items are present
        """
        if not self._inner:
            return None
        return self._inner[0]

    def push(self, item: T):
        """
        Push item onto the heap, maintaining the heap invariant.

        :param item: item to add to the heap
        """
        heappush(self._inner, item)

    def pop(self) -> Optional[T]:
        """
        Pop a smallest element from the heap, or return None if no elements are present.

        :return: a smallest element in the heap, or None if no items are present
        """
        if not self._inner:
            return None
        return heappop(self._inner)

    def __len__(self) -> int:
        return len(self._inner)

    def __getitem__(self, index: int) -> T:
        return self._inner[index]

    def __iter__(self) -> Generator[T, None, None]:
        yield from self._inner

    def __repr__(self) -> str:
        return repr(f"MinHeap({self._inner})")
