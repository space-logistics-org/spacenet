"""
This module defines schemas for specifying events which transport elements on the surface of
a body.
"""
from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from spacenet.schemas import ElementTransportEvent


__all__ = ["SurfaceTransport"]


class SurfaceTransport(ElementTransportEvent):
    """
    Schema for Surface Transport
    """

    name: str = Field(..., title="Name", description="The surface transport name")

    elements_id_list: List[UUID] = Field(
        ...,
        title="List of Element IDs",
        description="The list of IDs of elements being transported",
    )
    type: Literal["SurfaceTransport"]
