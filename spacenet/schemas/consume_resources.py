# -*- coding: utf-8 -*-
from .types import SafeInt
from pydantic import BaseModel, Field
from .resource import Resource


class ConsumeResource(BaseModel):
    removal_point_id: SafeInt = Field(..., title="Location ID",
                                      description="ID of the node or edge to remove "
                                                  "resources from")
    to_remove: Resource = Field(..., title="Consumed Resource",
                                description="resource to remove")
    quantity: float = Field(..., title="Consumed Quantity", description="quantity to remove")
