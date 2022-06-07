import doctest
from functools import reduce
from typing import Iterable, Set, Tuple, Union, TypeVar

from pydantic import BaseModel
from typing_extensions import Type

from ..schemas.constants import CREATE_SCHEMAS, READ_SCHEMAS, UPDATE_SCHEMAS

__all__ = ["union_from_iterable", "create_read_update_unions"]
T = TypeVar("T")


def union_from_iterable(it: Iterable[Type[T]]) -> Type[T]:
    """
    Provide a union over all of the types provided in the iterable ``it``.

    :param it: an iterable of types
    :return: Union[T0, T_1, ..., T_i] for all T_i in the provided iterable
    :raises ValueError: if provided iterable is empty

    The provided type bound is not tight, but a tighter bound can only really be expressed with
    variadic type arguments.

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
    schema_variants: Set[Type[BaseModel]],
) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
    """
    Partition the provided types in ``schema_variants`` into Create, Read, and Update schemas
    respectively.

    :param schema_variants: variants to partition
    :return: the types in ``schema_variants`` partitioned into Create, Read, and Update schemas

    >>> from app.database.api.schemas.resource import (
    ... ContinuousResource,
    ... DiscreteResource,
    ... ContinuousRead,
    ... DiscreteRead,
    ... ContinuousUpdate,
    ... DiscreteUpdate,
    ... )
    >>> resource_schemas = {
    ... ContinuousResource,
    ... DiscreteResource,
    ... ContinuousRead,
    ... DiscreteRead,
    ... ContinuousUpdate,
    ... DiscreteUpdate,
    ... }
    >>> (resource_create,
    ... resource_read,
    ... resource_update) = create_read_update_unions(resource_schemas)
    >>> Union[ContinuousResource, DiscreteResource] == resource_create
    True
    >>> Union[ContinuousRead, DiscreteRead] == resource_read
    True
    >>> Union[ContinuousUpdate, DiscreteUpdate] == resource_update
    True
    """
    return (
        union_from_iterable(schema_variants & CREATE_SCHEMAS),
        union_from_iterable(schema_variants & READ_SCHEMAS),
        union_from_iterable(schema_variants & UPDATE_SCHEMAS),
    )


if __name__ == "__main__":
    doctest.testmod()
