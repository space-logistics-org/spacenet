"""Defines object schemas for instantiated container elements."""

from typing import List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from ...resources import GenericResourceAmount, ResourceAmount
from ..element import ElementType
from .element import InstCargoCarrier


class InstResourceContainer(InstCargoCarrier):
    """
    Instantiated container for resources.
    """

    type: Literal[ElementType.RESOURCE_CONTAINER] = Field(
        ElementType.RESOURCE_CONTAINER, description="Element type"
    )
    contents: Optional[List[Union[GenericResourceAmount, ResourceAmount]]] = Field(
        None, title="Resource Amount", description="List of contained resource amounts"
    )
