import doctest
import random
from typing import Dict

#TODO: is this a self import?
from .utilities import TestingSessionLocal
from ....auth_dependencies import fastapi_users

__all__ = [
    "get_test_db",
    "get_current_user",
    "with_type",
    "make_subset",
    "first_subset_second",
    "filter_val_not_none",
]


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


get_current_user = fastapi_users.current_user(optional=True)


def with_type(d: Dict, kind) -> Dict:
    """
    Add or overwrite the key "type", associating it with kind, while not mutating original
    dict.

    :param d: dictionary to add "type": kind to
    :param kind: the kind of object dict represents
    :return: d | {"type": kind}
    >>> with_type({}, "foo") == {"type": "foo"}
    True
    >>> with_type({"a": "b"}, "bar") == {"a": "b", "type": "bar"}
    True
    >>> with_type({"a": "c", "type": "foo"}, "bar") == {"a": "c", "type": "bar"}
    True
    >>> d = {"a": "e"}
    >>> with_type(d, "baz") == {"a": "e", "type": "baz"}
    True
    >>> d == {"a": "e"}
    True
    """
    return {**d, "type": kind}


def make_subset(d: Dict) -> Dict:
    """
    From the dictionary d, make a subset of d without mutating d.

    :param d: dictionary to subset
    :return: subset of d
    A subset S is a dictionary D such that all key-value pairs in S are in D.

    >>> d = {"a": 5, "b": 5, "c": 10}
    >>> s = make_subset(d)
    >>> all((k in d and s[k] == d[k]) for k in s)
    True
    """
    ret = d.copy()
    for field in d:
        if random.random() < 0.25:
            del ret[field]
    return ret


def first_subset_second(first: Dict, second: Dict) -> bool:
    """
    Return true if first is a subset of second, false otherwise.

    :param first: first dict
    :param second: second dict
    :return: true if all elements in first are in second,
             and are mapped to same value, else false
    A subset S is a dictionary D such that all key-value pairs in S are in D.

    >>> subset = {"a": 1, "b": 5}
    >>> superset = {"a": 1, "b": 5, "c": 10}
    >>> first_subset_second(subset, superset)
    True
    >>> not_subsets = [{"a": 1, "b": 10}, {"a": 1, "d": 11}]
    >>> any(first_subset_second(s, superset) for s in not_subsets)
    False
    >>> first_subset_second({}, superset)
    True
    """
    return all(k in second and first[k] == second[k] for k in first)


def filter_val_not_none(d: Dict) -> Dict:
    """
    Return a new dictionary composed of all key-value pairs (k, v) in d where v is not None.

    :param d: original dictionary
    :return: d, without key-value pairs where value is None
    >>> filter_val_not_none({"a": 5, "b": 10, "c": None}) == {"a": 5, "b": 10}
    True
    """
    return {k: v for k, v in d.items() if v is not None}


if __name__ == "__main__":
    doctest.testmod()
