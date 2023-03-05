import doctest
from collections import defaultdict
from typing import Dict, Hashable, Mapping, Set, TypeVar

K = TypeVar("K")
HashableK = TypeVar("HashableK", bound=Hashable)
V = TypeVar("V", bound=Hashable)

__all__ = ["invert_map", "invert_injective_map"]


def invert_map(m: Mapping[HashableK, V]) -> Dict[V, Set[K]]:
    """
    Invert a mapping from K to V without mutating the provided input.

    :param m: any mapping from hashable keys to hashable values
    :return: a dict mapping v->ks where ks is all k in key-value pairs k->v in m
    >>> invert_map({1: 2, 3: 2}) == {2: {1, 3}}
    True
    """
    ret: defaultdict[V, Set[HashableK]] = defaultdict(set)
    for k, v in m.items():
        ret[v].add(k)
    return ret


def invert_injective_map(m: Mapping[K, V]) -> Dict[V, K]:
    """
    Invert an injective mapping from K to V without mutating the
    provided input.

    :param m: mapping from keys to one hashable value,
              where each value has only one associated key
    :return: a dict mapping v->k for all key-value pairs k->v in m
    >>> invert_injective_map({1: 2, 3: 4}) == {2: 1, 4: 3}
    True
    """
    assert len(set(m.values())) == len(
        m.values()
    ), "key-value mapping must be an injective function"
    return {v: k for k, v in m.items()}


if __name__ == "__main__":
    doctest.testmod()
