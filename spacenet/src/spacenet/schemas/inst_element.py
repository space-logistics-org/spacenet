"""
This module defines the schemas for Elements, and exports them explicitly.
"""
from abc import ABC
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import Extra, Field, confloat
from typing_extensions import Literal

from .types import SafeInt, SafeNonNegFloat, SafeNonNegInt
from .mixins import ImmutableBaseModel
from .constants import ClassOfSupply, Environment
from .state import StateUUID
from .inst_state import InstState, InstStateUUID
from .element import ElementKind

__all__ = [
    "InstElementUUID",
    "InstElement",
    "InstResourceContainer",
    "InstElementCarrier",
    "InstHumanAgent",
    "InstRoboticAgent",
    "InstPropulsiveVehicle",
    "InstSurfaceVehicle",
    "InstElementKind",
    "AllInstElements",
]

class InstElementUUID(ImmutableBaseModel):
    """
    A base class for instantiated elements defining only the UUID.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for instantiated element")


class InstElement(InstElementUUID):
    """
    A generic element.
    """
    template_id: UUID = Field(..., description="UUID of the template for this instantiated element")
    name: Optional[str] = Field(title="Name", description="name of the element")
    description: Optional[str] = Field(
        title="Description", description="short description of the element"
    )
    class_of_supply: Optional[ClassOfSupply] = Field(
        title="Class of Supply", description="class of supply number"
    )
    type: Optional[Literal[ElementKind.Element]] = Field(description="the element's type")
    environment: Optional[Environment] = Field(
        title="Environment", description="the element's environment"
    )
    accommodation_mass: Optional[SafeNonNegFloat] = Field(
        title="Accommodation Mass",
        description="the amount of additional COS5 "
        "required to pack the element inside a"
        " carrier.",
    )
    mass: Optional[SafeNonNegFloat] = Field(title="Mass", description="mass in kg")
    volume: Optional[SafeNonNegFloat] = Field(title="Volume", description="volume in m^3")
    states: Optional[List[InstState]] = Field(tile="States", description="list of states the element may possess")
    current_state: Optional[Union[StateUUID, InstStateUUID]] = Field(None, title="Current State", description="the current state of the element")

    class Config:
        """
        Configuration inner class forbidding additional fields
        """

        extra = Extra.forbid


class InstCargoCarrier(InstElement, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.
    """
    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        0, title="Max Cargo Mass", description="cargo capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        0, title="Maximum Cargo Volume", description="cargo capacity constraint (m^3)",
    )


class InstResourceContainer(InstCargoCarrier):
    """
    An element representing a container for resources.
    """

    type: Optional[Literal[ElementKind.ResourceContainer]] = Field(
        description="the element's type"
    )


class InstElementCarrier(InstCargoCarrier):
    """
    An element which can carry other elements.
    """
    cargo_environment: Optional[Environment] = Field(
        title="Cargo Environment",
        description="the cargo's environment — if "
        "unpressurized, "
        "cannot add pressurized elements as "
        "cargo",
    )


class InstAgent(InstElement, ABC):
    """
    An abstract base class representing a generic Agent element.
    """
    active_time_fraction: Optional[confloat(ge=0, le=1)] = Field(
        title="Active Time Fraction",
        description="the fraction of the day that an agent is active (available)",
    )


class InstHumanAgent(InstAgent):
    """
    An element representing a human agent, like a crew member.
    """
    pass

class InstRoboticAgent(InstAgent):
    """
    An element representing a robotic agent.
    """
    pass

class InstVehicle(InstCargoCarrier, ABC):
    """
    An abstract base class representing a generic Vehicle, surface or propulsive.
    """
    max_crew: Optional[SafeNonNegInt] = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class InstPropulsiveVehicle(InstVehicle):
    """
    An element representing a vehicle with its own propulsion.
    """

    type: Optional[Literal[ElementKind.PropulsiveVehicle]] = Field(
        description="the element's type"
    )
    isp: Optional[SafeNonNegFloat] = Field(
        title="Specific Impulse", description="specific impulse (s)"
    )
    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="maximum fuel (units)"
    )
    propellant_id: Optional[SafeInt]  # TODO: this needs constraints or to be an enum;
    #  perhaps a foreign key constraint in model?


class InstSurfaceVehicle(InstVehicle):
    """
    An element representing a surface vehicle.
    """

    type: Optional[Literal[ElementKind.SurfaceVehicle]] = Field(description="the element's type")
    max_speed: Optional[SafeNonNegFloat] = Field(
        title="Maximum Speed", description="maximum speed (kph)"
    )
    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="maximum fuel (units)"
    )
    fuel_id: Optional[SafeInt]  # TODO: this needs constraints or to be an enum;
    #  perhaps a foreign key constraint in model?


AllInstElements = Union[
    InstElement,
    InstResourceContainer,
    InstElementCarrier,
    InstHumanAgent,
    InstRoboticAgent,
    InstPropulsiveVehicle,
    InstSurfaceVehicle,
]
