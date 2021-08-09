from typing import List
from uuid import UUID

from pydantic import Field

from spacenet.schemas.mixins import ImmutableBaseModel


__all__ = [
    "ContainsElementRefs",
    "IndirectEntity"
]


class ContainsElementRefs(ImmutableBaseModel):
    contents: List[UUID] = Field(default_factory=list)


class IndirectEntity(ContainsElementRefs):
    inner: UUID
