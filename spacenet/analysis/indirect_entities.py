from typing import List
from uuid import UUID

from pydantic import Field, NonNegativeFloat

from spacenet.schemas import AllElements, AllNodes, AllUUIDEdges
from spacenet.schemas.mixins import ImmutableBaseModel


__all__ = [
    "IndirectEntity",
]


class ContainsElementRefs(ImmutableBaseModel):
    contents: List[UUID] = Field(default_factory=list)


class IndirectEntity(ContainsElementRefs):
    inner: UUID
