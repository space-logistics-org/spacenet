"""Defines object schemas for instantiated carrier elements."""

from typing import List, Union, Optional

from pydantic import Field
from typing_extensions import Literal

from .element import ElementType
from .inst_element import InstCargoCarrier, InstElementUUID

from ..utils import SafeNonNegFloat, SafeNonNegInt
from ..resources import ResourceAmount, GenericResourceAmount


class InstElementCarrier(InstCargoCarrier):
    """
    Instantiated carrier of other elements.

    :param [UUID] contents: list of instantiated elements (by unique identifiers) inside the carrier
    :param SafeNonNegInt max_crew: maximum number of human agents (crew)

    """

    type: Literal[ElementType.ELEMENT_CARRIER] = Field(
        ElementType.ELEMENT_CARRIER, description="Element type"
    )
    contents: List[InstElementUUID] = Field(
        [],
        title="Contents",
        description="List of instantiated elements (by unique identifiers) inside the carrier",
    )
    max_crew: Optional[SafeNonNegInt] = Field(
        title="Maximum Crew Count", description="Maximum number of human agents (crew)"
    )


class InstPropulsiveVehicle(InstElementCarrier):
    """
    Instantiated space vehicle with impulsive propulsion that can traverse space edges.

    :param SafeNonNegFloat isp: specific impulse (s, optional)
    :param SafeNonNegFloat max_fuel: maximum propellant amount (units, optional)
    :param ResourceAmount | GenericResourceAmount fuel: type and amount of propellant (optional)
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    isp: Optional[SafeNonNegFloat] = Field(
        title="Specific Impulse", description="specific impulse (s)"
    )
    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="maximum propellant amount (units)"
    )
    fuel: Optional[Union[ResourceAmount, GenericResourceAmount]] = Field(
        title="Propellant", description="type and amount of propellant"
    )


class InstSurfaceVehicle(InstElementCarrier):
    """
    Instantiated surface vehicle that can traverse surface edges.

    :param SafeNonNegFloat max_speed: maximum speed (km/hr, optional)
    :param SafeNonNegFloat max_fule: maximum fuel amount (units, optional)
    :param ResourceAmount | GenericResourceAmount fuel: type and amount of fuel

    """

    type: Literal[ElementType.SURFACE_VEHICLE] = Field(
        ElementType.SURFACE_VEHICLE, description="Element type"
    )
    max_speed: Optional[SafeNonNegFloat] = Field(
        title="Maximum Speed", description="Maximum speed (km/hr)"
    )
    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="Maximum fuel amount (units)"
    )
    fuel: Optional[Union[ResourceAmount, GenericResourceAmount]] = Field(
        title="Fuel", description="Type and amount of fuel"
    )
