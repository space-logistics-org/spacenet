"""Defines object schemas for carrier element templates."""

from typing import List, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from ...resources import GenericResourceAmount, ResourceAmount
from ..element import ElementType
from .element import CargoCarrier


class ElementCarrier(CargoCarrier):
    """
    Carrier of other elements.
    """

    type: Literal[ElementType.ELEMENT_CARRIER] = Field(
        ElementType.ELEMENT_CARRIER, description="Element type"
    )
    contents: List[UUID] = Field(
        [],
        title="Contents",
        description="List of elements (by unique identifiers) inside the carrier",
    )
    max_crew: int = Field(
        ...,
        title="Maximum Crew Count",
        description="Maximum number of human agents (crew)",
        ge=0,
    )


class PropulsiveVehicle(ElementCarrier):
    """
    Space vehicle with impulsive propulsion that can traverse space edges.
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    isp: float = Field(
        ..., title="Specific Impulse", description="Specific impulse (s)", ge=0
    )
    max_fuel: float = Field(
        ..., title="Maximum Fuel", description="Maximum propellant amount (units)", ge=0
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Fuel", description="Type and amount of propellant"
    )


class SurfaceVehicle(ElementCarrier):
    """
    Surface vehicle that can traverse surface edges.
    """

    type: Literal[ElementType.SURFACE_VEHICLE] = Field(
        ElementType.SURFACE_VEHICLE, description="the element's type"
    )
    max_speed: float = Field(
        ..., title="Maximum Speed", description="Maximum speed (km/hr)", ge=0
    )
    max_fuel: float = Field(
        ..., title="Maximum Fuel", description="Maximum fuel amount (units)", ge=0
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Fuel", description="Type and amount of fuel"
    )
