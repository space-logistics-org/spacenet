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
from .state import State, StateUUID
from .resource import ResourceAmount, GenericResourceAmount

__all__ = [
    "ElementKind",
    "ElementUUID",
    "Element",
    "CargoCarrier",
    "ResourceContainer",
    "ElementCarrier",
    "HumanAgent",
    "RoboticAgent",
    "PropulsiveVehicle",
    "SurfaceVehicle",
    "ElementKind",
    "AllElements"
]

class ElementKind(str, Enum):
    """
    An enumeration of all the types of Element
    """

    Element = "Element"
    ResourceContainer = "Resource Container"
    ElementCarrier = "Element Carrier"
    HumanAgent = "Human Agent"
    RoboticAgent = "Robotic Agent"
    PropulsiveVehicle = "Propulsive Vehicle"
    SurfaceVehicle = "Surface Vehicle"

class ElementUUID(ImmutableBaseModel):
    """
    A base class for elements defining only the UUID.

    :param UUID id: unique identifier for element
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for element")


class Element(ElementUUID):
    """
    A generic element.

    :param str name: name of the element
    :param str description: short description of the element
    :param ClassOfSupply class_of_supply: class of supply number
    :param Element type: the element's type
    :param Environment environment: the element's environment
    :param NonNegFloat accommodation_mass: the amount of additional COS5 required to pack the element inside a carrier
    :param NonNegFloat mass: mass in kg
    :param NonNegFloat volume: volume in cubic meters
    :param [State] states: list of states the element may possess
    :param SafeInt current_state_index: field describing the current state of the element.
    """

    name: str = Field(..., title="Name", description="name of the element")
    description: str = Field(
        ..., title="Description", description="short description of the element"
    )
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="class of supply number"
    )
    type: Literal[ElementKind.Element] = Field(ElementKind.Element, description="the element's type")
    environment: Environment = Field(
        ..., title="Environment", description="the element's environment"
    )
    accommodation_mass: SafeNonNegFloat = Field(
        ...,
        title="Accommodation Mass",
        description="the amount of additional COS5 "
        "required to pack the element inside a"
        " carrier.",
    )
    mass: SafeNonNegFloat = Field(..., title="Mass", description="mass in kg")
    volume: SafeNonNegFloat = Field(..., title="Volume", description="volume in m^3")
    states: List[State] = Field(..., tile="States", description="list of states the element may possess")
    current_state_index: SafeInt = Field(0, title="Current State", description="the current state of the element")
    icon: str = Field(..., title="icon", description="Icon of element")


    class Config:
        """
        Configuration inner class forbidding additional fields
        """

        extra = Extra.forbid


class CargoCarrier(Element, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.

    :param NonNegFloat max_cargo_mass: cargo capacity constraint (kg)
    :param max_cargo_volume: cargo capacity constraint (m^3)
    """

    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        0, title="Max Cargo Mass", description="cargo capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        0, title="Maximum Cargo Volume", description="cargo capacity constraint (m^3)",
    )


class ResourceContainer(CargoCarrier):
    """
    An element representing a container for resources.

    :param ResourceContainer type: the element's type
    """

    type: Literal[ElementKind.ResourceContainer] = Field(
        ElementKind.ResourceContainer, description="the element's type"
    )
    contents: List[Union[GenericResourceAmount, ResourceAmount]] = Field([], title="Resource Amount", description="list of resource quantities moved into container during spatial simulation")


class ElementCarrier(CargoCarrier):
    """
    An element which can carry other elements.

    :param Carrier type: the element's type
    :param Environment cargo_environment: the cargo's environment - if unpressurized, cannot add pressurized elements as cargo
    """

    type: Literal[ElementKind.ElementCarrier] = Field(ElementKind.ElementCarrier, description="the element's type")
    cargo_environment: Environment = Field(
        ...,
        title="Cargo Environment",
        description="the cargo's environment — if unpressurized, cannot add pressurized elements as cargo",
    )
    contents: List[ElementUUID] = Field([], title="Contents", description="list of elements moved into carrier during spatial simulation")


class Agent(Element, ABC):
    """
    An abstract base class representing a generic Agent element.

    :param active_time_fraction: the fraction of the day that an agent is active (available)
    :type active_time_fraction: float from 0 to 1
    """

    active_time_fraction: confloat(ge=0, le=1) = Field(
        ...,
        title="Active Time Fraction",
        description="the fraction of the day that an agent is active (available)",
    )


class HumanAgent(Agent):
    """
    An element representing a human agent, like a crew member.

    :param HumanAgent type: the element's type
    """

    type: Literal[ElementKind.HumanAgent] = Field(ElementKind.HumanAgent, description="the element's type")


class RoboticAgent(Agent):
    """
    An element representing a robotic agent.

    :param RoboticAgent type: the element's type
    """

    type: Literal[ElementKind.RoboticAgent] = Field(ElementKind.RoboticAgent, description="the element's type")


class Vehicle(CargoCarrier, ABC):
    """
    An abstract base class representing a generic Vehicle, surface or propulsive.

    :param NonNegInt max_crew: crew capacity constraint
    """

    max_crew: SafeNonNegInt = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class PropulsiveVehicle(Vehicle):
    """
    An element representing a vehicle with its own propulsion.

    :param PropulsiveVehicle type: the element's type
    :param NonNegFloat isp: "specific impulse (s)
    :param NonNegFloat max_fuel: maximum fuel (units)
    :param propellant ResourceAmount: UUID of propellant resource and rate of usage
    """

    type: Literal[ElementKind.PropulsiveVehicle] = Field(
        ElementKind.PropulsiveVehicle, description="the element's type"
    )
    isp: SafeNonNegFloat = Field(
        ..., title="Specific Impulse", description="specific impulse (s)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    #TODO: could this also be GenericResourceAmount?
    propellant: ResourceAmount = Field(..., title="Propellant", description="UUID of propellant resource and rate")


class SurfaceVehicle(Vehicle):
    """
    An element representing a surface vehicle.

    :param SurfaceVehicle type: the element's type
    :param NonNegFloat max_speed: maximum speed (kph)
    :param NonNegFloat max_fule: maximum fuel (units)
    """

    type: Literal[ElementKind.SurfaceVehicle] = Field(ElementKind.SurfaceVehicle, description="the element's type")
    max_speed: SafeNonNegFloat = Field(
        ..., title="Maximum Speed", description="maximum speed (kph)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    #TODO: could this also be GenericResourceAmount?
    propellant: ResourceAmount = Field(..., title="Propellant", description="UUID of propellant resource and rate")


AllElements = Union[
    Element,
    ResourceContainer,
    ElementCarrier,
    HumanAgent,
    RoboticAgent,
    PropulsiveVehicle,
    SurfaceVehicle,
]