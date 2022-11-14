"""
Locations provide a generic base class for network nodes and edges.
"""

from abc import ABC
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..elements import AllInstElements


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
    contents: List[AllInstElements] = Field(
        [],
        title="Contents",
        description="List of elements located at this location.",
    )

    def add_element(self, element: AllInstElements) -> None:
        """
        Add an element to this location.

        Args:
            element (:obj:`InstElementUUID`): The element instance to add.
        """
        if element not in self.contents:
            self.contents.append(element)

    def remove_element(self, element: AllInstElements) -> None:
        """
        Remove an element from this location.

        Args:
            element (:obj:`InstElementUUID`): The element instance to remove.
        """
        self.contents.remove(element)
