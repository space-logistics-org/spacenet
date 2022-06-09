# -*- coding: utf-8 -*-
"""
This module defines a schema for consuming resources from a given point.
"""
from uuid import UUID
from typing import Union

from pydantic import Field

from . import Event
from .inst_element import InstElementUUID
from .resource import ResourceAmount, GenericResourceAmount


__all__ = ["ConsumeResources"]


class ConsumeResources(Event):
    """
    Schema for consuming resources from a point

    :param ResourceAmount | GenericResourceAmount resources: list of resource quantities to consume
    :param InstElementUUID source: UUID of the instantiated element where the resource to be consumed is currently stored
    """


    resources: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Consumed Resources", description="list of resource quantities to consume"
    )
    source: InstElementUUID = Field(
        ..., title="Consumed Quantity", description="UUID of the instantiated element where the resource to be consumed is currently stored"
    )
