"""
Locations provide a generic base class for network nodes and edges.
"""

from abc import ABC
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..elements import InstElementUUID


class LocationUUID(CamelModel):
    """
    Location referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Location(LocationUUID, ABC):
    """
    Abstract base class for a network location.
    """

    name: str = Field(..., title="Name", description="Location name")
    description: Optional[str] = Field(
        default=None,
        title="Description",
        description="Short description of this location.",
    )
    contents: List[InstElementUUID] = Field(
        [],
        title="Contents",
        description="List of elements (by unique identifiers) located at this location.",
    )
