# -*- coding: utf-8 -*-
from uuid import UUID

from pydantic import Field

from . import Event
from .resource import Resource
from .types import SafeFloat


__all__ = [
    "ConsumeResource"
]


class ConsumeResource(Event):
    removal_point_id: UUID = Field(
        ...,
        title="Location ID",
        description="ID of the node or edge to remove " "resources from",
    )
    to_remove: Resource = Field(
        ..., title="Consumed Resource", description="resource to remove"
    )
    quantity: SafeFloat = Field(
        ..., title="Consumed Quantity", description="quantity to remove"
    )
