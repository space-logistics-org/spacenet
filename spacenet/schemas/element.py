"""
This module defines the schemas for Elements, and exports them explicitly.
"""
from abc import ABC
from enum import Enum
from math import inf
from typing import Optional

from pydantic import BaseModel, Field, confloat, conint
from typing_extensions import Literal

from ..constants import Environment, ClassOfSupply, SQLITE_MAX_INT, SQLITE_MIN_INT

__all__ = [
    "Element",
    "ResourceContainer",
    "ElementCarrier",
    "HumanAgent",
    "RoboticAgent",
    "PropulsiveVehicle",
    "SurfaceVehicle",
    "ElementKind",
]


class ElementKind(str, Enum):
    """
    An enumeration of all the types of Element.
    """

    Element = "Element"
    ResourceContainer = "ResourceContainer"
    ElementCarrier = "ElementCarrier"
    HumanAgent = "HumanAgent"
    RoboticAgent = "RoboticAgent"
    Propulsive = "Propulsive"
    Surface = "Surface"


class Element(BaseModel):
    """
    A generic element.
    """

    name: str = Field(..., title="Name", description="name of the element")
    description: str = Field(
        ..., title="Description", description="short description of the element"
    )
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="class of supply number"
    )
    type: Literal[ElementKind.Element] = Field(description="the element's type")
    environment: Environment = Field(
        ..., title="Environment", description="the element's environment"
    )
    accommodation_mass: confloat(ge=0, lt=inf) = Field(
        ...,
        title="Accommodation Mass",
        description="the amount of additional COS5 "
        "required to pack the element inside a"
        " carrier.",
    )
    mass: confloat(ge=0, lt=inf) = Field(..., title="Mass", description="mass in kg")
    volume: confloat(ge=0, lt=inf) = Field(
        ..., title="Volume", description="volume in m^3"
    )


class CargoCarrier(Element, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.
    """

    max_cargo_mass: Optional[confloat(ge=0, lt=inf)] = Field(
        ..., title="Max Cargo Mass", description="cargo capacity constraint (kg)"
    )
    max_cargo_volume: Optional[confloat(ge=0, lt=inf)] = Field(
        ...,
        title="Maximum Cargo Volume",
        description="cargo capacity constraint (m^3)",
    )


class ResourceContainer(CargoCarrier):
    """
    An element representing a container for resources.
    """

    type: Literal[ElementKind.ResourceContainer] = Field(
        description="the element's type"
    )


class ElementCarrier(CargoCarrier):
    """
    An element which can carry other elements.
    """

    type: Literal[ElementKind.ElementCarrier] = Field(description="the element's type")
    cargo_environment: Environment = Field(
        ...,
        title="Cargo Environment",
        description="the cargo's environment — if "
        "unpressurized, "
        "cannot add pressurized elements as "
        "cargo",
    )


class Agent(Element, ABC):
    """
    An abstract base class representing a generic Agent element.
    """

    active_time_fraction: confloat(ge=0, le=1) = Field(
        ...,
        title="Active Time Fraction",
        description="the fraction of the day that an agent is active (available)",
    )


class HumanAgent(Agent):
    """
    An element representing a human agent, like a crew member.
    """

    type: Literal[ElementKind.HumanAgent] = Field(description="the element's type")


class RoboticAgent(Agent):
    """
    An element representing a robotic agent.
    """

    type: Literal[ElementKind.RoboticAgent] = Field(description="the element's type")


class Vehicle(CargoCarrier, ABC):
    """
    An abstract base class representing a generic Vehicle, surface or propulsive.
    """

    max_crew: conint(strict=True, ge=0, le=SQLITE_MAX_INT) = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class PropulsiveVehicle(Vehicle):
    """
    An element representing a vehicle with its own propulsion.
    """

    type: Literal[ElementKind.Propulsive] = Field(description="the element's type")
    isp: confloat(ge=0, lt=inf) = Field(
        ..., title="Specific Impulse", description="specific impulse (s)"
    )
    max_fuel: confloat(ge=0, lt=inf) = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    propellant_id: conint(
        strict=True, ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT
    )  # TODO: this needs constraints or to be an enum;
    #  perhaps a foreign key constraint in model?


class SurfaceVehicle(Vehicle):
    """
    An element representing a surface vehicle.
    """

    type: Literal[ElementKind.Surface] = Field(description="the element's type")
    max_speed: confloat(ge=0, lt=inf) = Field(
        ..., title="Maximum Speed", description="maximum speed (kph)"
    )
    max_fuel: confloat(ge=0, lt=inf) = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    fuel_id: conint(
        strict=True, ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT
    )  # TODO: this needs constraints or to be an enum;
    #  perhaps a foreign key constraint in model?
