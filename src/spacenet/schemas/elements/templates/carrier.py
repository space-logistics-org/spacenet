"""Defines object schemas for carrier element templates."""

from typing import Any, List
from uuid import UUID

from pydantic import Field, field_validator, model_validator
from typing_extensions import Literal

from ..element import ElementType
from ..propulsion import (
    PropulsionSystem,
    ResourceTank,
    check_propulsion_systems,
    upgrade_vehicle,
)
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
    Space vehicle with one or more impulsive propulsion systems that can
    traverse space edges.
    """

    type: Literal[ElementType.PROPULSIVE_VEHICLE] = Field(
        ElementType.PROPULSIVE_VEHICLE, description="Element type"
    )
    propulsion_systems: List[PropulsionSystem] = Field(
        ...,
        title="Propulsion Systems",
        description="List of propulsion systems (each with a specific impulse "
        "and a fuel tank) with distinct types",
        min_length=1,
    )

    @model_validator(mode="before")
    @classmethod
    def _upgrade(cls, data: Any) -> Any:
        return upgrade_vehicle(data, propulsive=True)

    _check_systems = field_validator("propulsion_systems")(check_propulsion_systems)


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
    fuel_tank: ResourceTank = Field(
        ..., title="Fuel Tank", description="Fuel tank (type and amount of fuel)"
    )

    @model_validator(mode="before")
    @classmethod
    def _upgrade(cls, data: Any) -> Any:
        return upgrade_vehicle(data, propulsive=False)
