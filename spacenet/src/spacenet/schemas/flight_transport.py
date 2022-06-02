"""
This module defines a schema for specifying flight transport events, representing cases where
a vehicle is known to be able to traverse the given edge.
"""
from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from spacenet.schemas import ElementTransportEvent
from .inst_element import InstElementUUID


__all__ = ["FlightTransport"]


class FlightTransport(ElementTransportEvent):
    """
    Schema for Flight Transport
    """

    name: str = Field(..., title="Name", description="The flight transport name")

    elements: List[InstElementUUID] = Field(
        ...,
        title="List of Instantiated Element UUIDs",
        description="The list of UUIDs of instantiated elements being transported",
    )
    type: Literal["FlightTransport"]
