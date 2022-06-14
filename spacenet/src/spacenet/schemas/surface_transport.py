"""
This module defines schemas for specifying events which transport elements on the surface of
a body.
"""
from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from .bases import ElementTransportEvent, EventType
from .inst_element import InstElementUUID



__all__ = ["SurfaceTransport"]


class SurfaceTransport(ElementTransportEvent):
    """
    Schema for Surface Transport

    :param SurfaceTransport type: type of event occuring
    :param [InstElementUUID] elements: the list of UUIDs of instantiated elements being transported
    """
    type: Literal[EventType.SurfaceTransport] = Field(
        EventType.SurfaceTransport, title="Type", description="Type of event",
    )
    elements: List[InstElementUUID] = Field(
        ...,
        title="List of Element UUIDs",
        description="The list of IDs of instantiated elements being transported",
    )
