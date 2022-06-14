"""
This module defines a schema for specifying flight transport events, representing cases where
a vehicle is known to be able to traverse the given edge.
"""
from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from .bases import ElementTransportEvent, EventType
from .inst_element import InstElementUUID


__all__ = ["FlightTransport"]


class FlightTransport(ElementTransportEvent):
    """
    Schema for Flight Transport

    :param FlightTransport type: type of event
    :param [InstElementUUID] elements: list of UUIDs of instantiated elements being transported
    """
    type: Literal[EventType.FlightTransport] = Field(
        EventType.FlightTransport, title="Type", description="Type of event",
    )

    elements: List[InstElementUUID] = Field(
        ...,
        title="List of Instantiated Element UUIDs",
        description="The list of UUIDs of instantiated elements being transported",
    )
