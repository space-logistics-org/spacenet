"""
This module defines simulation entities using identifiers references rather than values
directly.
"""
from typing import List
from uuid import UUID

from pydantic import Field

from spacenet.schemas.mixins import ImmutableBaseModel


__all__ = [
    "IndirectEntity",
]


class ContainsElementRefs(ImmutableBaseModel):
    """
    A mixin schema providing a list of contained elements by their UUIDs.
    """

    contents: List[UUID] = Field(default_factory=list)


class IndirectEntity(ContainsElementRefs):
    """
    An entity containing elements by their UUIDs and storing its inner value by a UUID as well.
    """

    inner: UUID
