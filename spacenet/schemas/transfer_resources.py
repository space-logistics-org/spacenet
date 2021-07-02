from typing import List
from .types import SafeInt
from pydantic import BaseModel, Field



__all__ = ["TransferResourcesEvent"]

class TransferResourcesEvent(BaseModel):

    """
    An event that moves resources at a specific time and location (node or edge)
    from an origin resource container to a destination resource container
    """

    to_transfer: List[SafeInt] = Field(..., description = "the list of resource IDs to transfer")

    origin_id: SafeInt = Field(..., description = "the ID of the original time and location which the resources are being transferred from")

    destination_id: SafeInt = Field(..., description = "the ID of the new location which the elements are being transferred to")
    
    
