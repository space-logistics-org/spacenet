"""Defines object schemas for carrier element templates."""

from typing import List, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .element import CargoCarrier, ElementType

from ..utils import SafeNonNegFloat, SafeNonNegInt
from ..resources import ResourceAmount, GenericResourceAmount


class ElementCarrier(CargoCarrier):
    """
    Carrier of other elements.

    :param [UUID] contents: list of elements (by unique identifiers) inside the carrier
    :param SafeNonNegInt max_crew: maximum number of human agents (crew)
    """

    type: Literal[ElementType.ELEMENT_CARRIER] = Field(
        ElementType.ELEMENT_CARRIER, description="Element type"
    )
    contents: List[UUID] = Field(
        [],
        title="Contents",
        description="List of elements (by unique identifiers) inside the carrier",
    )
    max_crew: SafeNonNegInt = Field(
        ...,
        title="Maximum Crew Count",
        description="Maximum number of human agents (crew)",
    )


class PropulsiveVehicle(ElementCarrier):
    """
    Space vehicle with impulsive propulsion that can traverse space edges.

    :param SafeNonNegFloat isp: specific impulse (s)
    :param SafeNonNegFloat max_fuel: maximum propellant amount (units)
    :param Union[ResourceAmount, GenericResourceAmount] fuel: type and amount of propellant
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    isp: SafeNonNegFloat = Field(
        ..., title="Specific Impulse", description="Specific impulse (s)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="Maximum propellant amount (units)"
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Fuel", description="Type and amount of propellant"
    )


class SurfaceVehicle(ElementCarrier):
    """
    Surface vehicle that can traverse surface edges.

    :param SafeNonNegFloat max_speed: maximum speed (km/hr)
    :param SafeNonNegFloat max_fuel: maximum fuel amount (units)
    :param Union[ResourceAmount, GenericResourceAmount] fuel: type and amount of fuel
    """

    type: Literal[ElementType.SURFACE_VEHICLE] = Field(
        ElementType.SURFACE_VEHICLE, description="the element's type"
    )
    max_speed: SafeNonNegFloat = Field(
        ..., title="Maximum Speed", description="Maximum speed (km/hr)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="Maximum fuel amount (units)"
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Fuel", description="Type and amount of fuel"
    )
