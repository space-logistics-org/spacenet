"""Defines object schemas for instantiated carrier elements."""

from typing import List, Optional

from pydantic import Field, field_validator
from typing_extensions import Literal

from ..element import ElementType
from ..propulsion import PropulsionSystem, ResourceTank, check_propulsion_systems
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
    Instantiated space vehicle with one or more impulsive propulsion systems
    that can traverse space edges.
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    propulsion_systems: Optional[List[PropulsionSystem]] = Field(
        None,
        title="Propulsion Systems",
        description="List of propulsion systems (each with a specific impulse "
        "and a fuel tank) with distinct types which replaces the list of "
        "the element template",
        min_length=1,
    )

    _check_systems = field_validator("propulsion_systems")(check_propulsion_systems)


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
    fuel_tank: Optional[ResourceTank] = Field(
        None, title="Fuel Tank", description="Fuel tank (type and amount of fuel)"
    )
    fuel_consumption: Optional[float] = Field(
        None,
        title="Fuel Consumption",
        description="Fuel (units) consumed per kilometer traversed",
        ge=0,
    )
    energy_consumption: Optional[float] = Field(
        None,
        title="Energy Consumption",
        description="Stored energy (kWh) consumed per kilometer traversed",
        ge=0,
    )
    max_crewed_duration: Optional[float] = Field(
        None,
        title="Max Crewed Traverse",
        description="Longest traverse (hours) with crew aboard, e.g., the EVA suit "
        "endurance of an unpressurized rover (omitted if unlimited)",
        ge=0,
    )
    walk_back_distance: Optional[float] = Field(
        None,
        title="Walk-Back Distance",
        description="Greatest distance (km) which crew of an unpressurized rover "
        "may travel from a pressurized safe haven (omitted if unlimited)",
        ge=0,
    )
