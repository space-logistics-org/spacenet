from typing import List
from typing_extensions import Literal
from uuid import UUID

from pydantic import Field

from spacenet.schemas import ElementTransportEvent


__all__ = ["FlightTransport"]


class FlightTransport(ElementTransportEvent):

    # Schema for Flight Transport

    name: str = Field(..., title="Name", description="The flight transport name")

    elements_id_list: List[UUID] = Field(
        ...,
        title="List of Element IDs",
        description="The list of IDs of elements being transported",
    )
    type: Literal["FlightTransport"]
