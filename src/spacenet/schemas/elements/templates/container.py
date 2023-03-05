"""Defines object schemas for container element templates."""

from typing import List, Union

from pydantic import Field
from typing_extensions import Literal

from ...resources import GenericResourceAmount, ResourceAmount
from ..element import ElementType
from .element import CargoCarrier


class ResourceContainer(CargoCarrier):
    """
    Container for resources.
    """

    type: Literal[ElementType.RESOURCE_CONTAINER] = Field(
        ElementType.RESOURCE_CONTAINER, description="Element type"
    )
    contents: List[Union[GenericResourceAmount, ResourceAmount]] = Field(
        [], title="Resource Amount", description="List of contained resource amounts"
    )
