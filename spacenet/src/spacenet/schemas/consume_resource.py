# -*- coding: utf-8 -*-
"""
This module defines a schema for consuming resources from a given point.
"""
from uuid import UUID
from typing import Union

from pydantic import Field

from . import Event
from .resource import Resource
from .types import SafeFloat
from .node import NodeUUID
from .edge import EdgeUUID
from .resource import ResourceAmount, GenericResourceAmount


__all__ = ["ConsumeResource"]


class ConsumeResource(Event):
    """
    Schema for consuming resources from a point

    :param NodeUUID | EdgeUUID location: ID of the node or edge to remove resources from
    :param ResourceUUID to_remove: UUID of resource to remove
    :param float quantity: quantity to remove
    """

    location: Union[NodeUUID, EdgeUUID] = Field(
        ...,
        title="Location ID",
        description="ID of the node or edge to remove resources from",
    )
    resources: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Consumed Resource", description="UUID of resource to remove"
    )
    quantity: SafeFloat = Field(
        ..., title="Consumed Quantity", description="quantity to remove"
    )
