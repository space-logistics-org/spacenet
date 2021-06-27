import doctest
from functools import reduce
from typing import Iterable, Set, Tuple, TypeVar, Union

from pydantic.main import Model
from typing_extensions import Type

from ..schemas.constants import CREATE_SCHEMAS, READ_SCHEMAS, UPDATE_SCHEMAS

__all__ = ["union_from_iterable", "create_read_update_unions"]

T = TypeVar("T")


def union_from_iterable(it: Iterable[Type[T]]) -> Union[Type[T]]:
    """
    Provide a union over all of the types provided in the iterable "it".

    :param it: an iterable of types
    :return: Union[T0, T_1, T_i] for all T_i in "it"
    :raises ValueError: if provided iterable is non-empty
    >>> union_from_iterable([int, str]) == Union[int, str]
    True
    >>> try:
    ...     union_from_iterable(())
    ... except ValueError:
    ...     pass
    ... else:
    ...     assert False
    >>> union_from_iterable((bool, )) == Union[bool]
    True
    >>> union_from_iterable((bool, )) == bool
    True
    """
    iterator = it.__iter__()
    try:
        first = Union[next(iterator)]
    except StopIteration:
        raise ValueError("Provided iterable must be non-empty")
    return reduce(lambda acc, ty: Union[acc, ty], iterator, first)


def create_read_update_unions(
        schema_variants: Set[Type],
) -> Tuple[Union[Type[Model]], Union[Type[Model]], Union[Type[Model]]]:
    return (
        union_from_iterable(schema_variants & CREATE_SCHEMAS),
        union_from_iterable(schema_variants & READ_SCHEMAS),
        union_from_iterable(schema_variants & UPDATE_SCHEMAS),
    )


if __name__ == "__main__":
    doctest.testmod()
