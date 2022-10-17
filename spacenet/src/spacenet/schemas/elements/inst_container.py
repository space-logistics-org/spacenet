"""Defines object schemas for instantiated container elements."""

from typing import List, Union, Optional

from pydantic import Field
from typing_extensions import Literal

from .element import ElementType
from .inst_element import InstCargoCarrier

from ..resources import ResourceAmount, GenericResourceAmount


class InstResourceContainer(InstCargoCarrier):
    """
    Instantiated container for resources.

    :param ResourceContainer type: the element's type
    :param List[Union[GenericResourceAmount, ResourceAmount]] contents: list of contained resource amounts (optional)
    """

    type: Literal[ElementType.RESOURCE_CONTAINER] = Field(
        ElementType.RESOURCE_CONTAINER, description="Element type"
    )
    contents: Optional[List[Union[GenericResourceAmount, ResourceAmount]]] = Field(
        title="Resource Amount", description="List of contained resource amounts"
    )
