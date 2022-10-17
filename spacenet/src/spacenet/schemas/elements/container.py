"""Defines object schemas for container element templates."""

from typing import List, Union

from pydantic import Field
from typing_extensions import Literal

from .element import CargoCarrier, ElementType

from ..resources import ResourceAmount, GenericResourceAmount


class ResourceContainer(CargoCarrier):
    """
    Container for resources.

    :param List[Union[GenericResourceAmount, ResourceAmount]] contents: list of contained resource amounts
    """

    type: Literal[ElementType.RESOURCE_CONTAINER] = Field(
        ElementType.RESOURCE_CONTAINER, description="Element type"
    )
    contents: List[Union[GenericResourceAmount, ResourceAmount]] = Field(
        [], title="Resource Amount", description="List of contained resource amounts"
    )
