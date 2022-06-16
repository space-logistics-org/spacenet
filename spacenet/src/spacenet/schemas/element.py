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
    "ElementType",
    "ElementUUID",
    "Element",
    "CargoCarrier",
    "ResourceContainer",
    "ElementCarrier",
    "HumanAgent",
    "RoboticAgent",
    "PropulsiveVehicle",
    "SurfaceVehicle",
    "ElementType",
    "AllElements"
]

class ElementType(str, Enum):
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
    :param Environment environment: the element's environment, either unpressurized or pressurized
    :param SafeNonNegFloat accommodation_mass: the amount of additional COS5 required to pack the element inside a carrier
    :param SafeNonNegFloat mass: mass in kg
    :param SafeNonNegFloat volume: volume in cubic meters
    :param [State] states: list of states the element may possess
    :param SafeInt current_state_index: The index of the current state of the element. Initialized at the initial state.
    """

    name: str = Field(..., title="Name", description="Name of the element")
    description: str = Field(
        ..., title="Description", description="Short description of the element"
    )
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply number"
    )
    type: Literal[ElementType.Element] = Field(ElementType.Element, description="The element's type")
    environment: Environment = Field(
        ..., title="Environment", description="The element's environment, either unpressurized or pressurized"
    )
    accommodation_mass: SafeNonNegFloat = Field(
        ...,
        title="Accommodation Mass",
        description="The amount of additional COS5 "
        "required to pack the element inside a"
        " carrier.",
    )
    mass: SafeNonNegFloat = Field(..., title="Mass", description="Mass in kg")
    volume: SafeNonNegFloat = Field(..., title="Volume", description="Volume in m^3")
    states: List[State] = Field(..., title="States", description="List of states the element may possess")
    current_state_index: SafeInt = Field(0, title="Current State", description="The index of the current state of the element. Initialized at the initial state")
    #TODO: parts and icons are currently hidden and not implemented in SpaceNet Cloud
    parts: Optional[List] = Field(title="Parts filler")
    icon: Optional[str] = Field(title="string of icon")


    class Config:
        """
        Configuration inner class forbidding additional fields
        """

        extra = Extra.forbid


class CargoCarrier(Element, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.

    :param SafeNonNegFloat max_cargo_mass: cargo capacity constraint (kg)
    :param SafeNonNegFloat max_cargo_volume: cargo capacity constraint (m^3)
    :param Environment cargo_environment: the cargo's environment - if unpressurized, cannot add pressurized elements as cargo
    """

    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        0, title="Max Cargo Mass", description="Cargo capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        0, title="Maximum Cargo Volume", description="Cargo capacity constraint (m^3)",
    )
    cargo_environment: Environment = Field(
        ...,
        title="Cargo Environment",
        description="The cargo's environment — if unpressurized, cannot add pressurized elements as cargo",
    )


class ResourceContainer(CargoCarrier):
    """
    An element representing a container for resources.

    :param ResourceContainer type: the element's type
    :param [ResourceAmount | GenericResourceAmount] contents: list of resource quantities initially in container
    """

    type: Literal[ElementType.ResourceContainer] = Field(
        ElementType.ResourceContainer, description="The element's type"
    )
    contents: List[Union[GenericResourceAmount, ResourceAmount]] = Field([], title="Resource Amount", description="List of resource quantities initially in container")


class ElementCarrier(CargoCarrier):
    """
    An element which can carry other elements.

    :param ElementCarrier type: the element's type
    :param [UUID] contents: list of elements initially in carrier. These should be UUIDs of element templates.
    :param SafeNonNegInt max_crew: crew capacity constraint
    """

    type: Literal[ElementType.ElementCarrier] = Field(ElementType.ElementCarrier, description="the element's type")
    contents: List[UUID] = Field([], title="Contents", description="List of elements initially in carrier")
    max_crew: SafeNonNegInt = Field(
        ..., title="Maximum Crew Count", description="Crew capacity constraint"
    )


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

    type: Literal[ElementType.HumanAgent] = Field(ElementType.HumanAgent, description="the element's type")


class RoboticAgent(Agent):
    """
    An element representing a robotic agent.

    :param RoboticAgent type: the element's type
    """

    type: Literal[ElementType.RoboticAgent] = Field(ElementType.RoboticAgent, description="the element's type")

#TODO: should vehicles inherit from element carriers?


class PropulsiveVehicle(ElementCarrier):
    """
    An element representing a vehicle with its own propulsion.

    :param PropulsiveVehicle type: the element's type
    :param SafeNonNegFloat isp: specific impulse (s)
    :param SafeNonNegFloat max_fuel: the maximum amount of fuel which can be stored in the propulsive vehicle (units)
    :param ResourceAmount | GenericResourceAmount fuel: UUID and amount of fuel used by propulsive vehicle
    """
#TODO: check max fuel description is correct
    type: Literal[ElementType.PropulsiveVehicle] = Field(
        ElementType.PropulsiveVehicle, description="the element's type"
    )
    isp: SafeNonNegFloat = Field(
        ..., title="Specific Impulse", description="specific impulse (s)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(..., title="Fuel", description="UUID and amount of fuel used by propulsive vehicle")


class SurfaceVehicle(ElementCarrier):
    """
    An element representing a surface vehicle.

    :param SurfaceVehicle type: the element's type
    :param SafeNonNegFloat max_speed: maximum speed (kph)
    :param SafeNonNegFloat max_fuel: maximum fuel (units)
    :param ResourceAmount | GenericResourceAmount fuel: UUID and amount of propellant used by surface vehicle

    """
#TODO: clarify description
    type: Literal[ElementType.SurfaceVehicle] = Field(ElementType.SurfaceVehicle, description="the element's type")
    max_speed: SafeNonNegFloat = Field(
        ..., title="Maximum Speed", description="maximum speed (kph)"
    )
    max_fuel: SafeNonNegFloat = Field(
        ..., title="Maximum Fuel", description="maximum fuel (units)"
    )
    fuel: Union[ResourceAmount, GenericResourceAmount] = Field(..., title="Fuel", description="UUID and rate of fuel used by surface vehicle")


AllElements = Union[
    Element,
    ResourceContainer,
    ElementCarrier,
    HumanAgent,
    RoboticAgent,
    PropulsiveVehicle,
    SurfaceVehicle,
]