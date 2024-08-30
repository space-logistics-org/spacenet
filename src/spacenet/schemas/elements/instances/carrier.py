"""Defines object schemas for instantiated carrier elements."""

from typing import List, Optional, Union

from pydantic import Field
from typing_extensions import Literal

from ...resources import GenericResourceAmount, ResourceAmount
from ..element import ElementType
from .element import InstCargoCarrier, InstElementUUID


class InstElementCarrier(InstCargoCarrier):
    """
    Instantiated carrier of other elements.

    """

    type: Literal[ElementType.ELEMENT_CARRIER] = Field(
        ElementType.ELEMENT_CARRIER, description="Element type"
    )
    contents: List[InstElementUUID] = Field(
        [],
        title="Contents",
        description="List of instantiated elements (by unique identifiers) inside the carrier",
    )
    max_crew: Optional[int] = Field(
        None, title="Maximum Crew Count",
        description="Maximum number of human agents (crew)",
        ge=0,
    )


class InstPropulsiveVehicle(InstElementCarrier):
    """
    Instantiated space vehicle with impulsive propulsion that can traverse space edges.
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    isp: Optional[float] = Field(
        None, title="Specific Impulse", description="specific impulse (s)", ge=0
    )
    max_fuel: Optional[float] = Field(
        None, title="Maximum Fuel", description="maximum propellant amount (units)", ge=0
    )
    fuel: Optional[Union[ResourceAmount, GenericResourceAmount]] = Field(
        None, title="Propellant", description="type and amount of propellant"
    )


class InstSurfaceVehicle(InstElementCarrier):
    """
    Instantiated surface vehicle that can traverse surface edges.

    """

    type: Literal[ElementType.SURFACE_VEHICLE] = Field(
        ElementType.SURFACE_VEHICLE, description="Element type"
    )
    max_speed: Optional[float] = Field(
        None, title="Maximum Speed", description="Maximum speed (km/hr)", ge=0
    )
    max_fuel: Optional[float] = Field(
        None, title="Maximum Fuel", description="Maximum fuel amount (units)", ge=0
    )
    fuel: Optional[Union[ResourceAmount, GenericResourceAmount]] = Field(
        None, title="Fuel", description="Type and amount of fuel"
    )
