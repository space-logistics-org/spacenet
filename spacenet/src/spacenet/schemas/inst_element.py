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
from .element import ElementType, ElementUUID
from .resource import ResourceAmount, GenericResourceAmount, ResourceAmountRate
from .constants import ClassOfSupply

__all__ = [
    "InstElementUUID",
    "InstElement",
    "InstResourceContainer",
    "InstElementCarrier",
    "InstHumanAgent",
    "InstRoboticAgent",
    "InstPropulsiveVehicle",
    "InstSurfaceVehicle",
    "InstElementType",
    "AllInstElements",
]

class InstElementUUID(ImmutableBaseModel):
    """
    A base class for instantiated elements defining only the UUID.

    :param UUID id: unique identifier for element

    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for instantiated element")


class InstElement(InstElementUUID):
    """
    A generic element.

    :param ElementUUID template_id: UUID of the template for this instantiated element
    :param str name: name of the instantiated element
    :param str description: short description of the element (optional)
    :param ClassOfSupply class_of_supply: class of supply number (optional)
    :param Environment environment: the element's environment (optional)
    :param SafeNonNegFloat accommodation_mass: the amount of additional COS5 required to pack the element inside a carrier (optional)
    :param SafeNonNegFloat mass: mass in kg (optional)
    :param SafeNonNegFloat volume: volume in cubic meters (optional)
    :param [State] states: list of states the instantiated element may possess (optional)
    :param SafeInt current_state_index: field describing the current state of the element. Set to initial state during creation. (optional)
    """

    template_id: ElementUUID = Field(..., description="UUID of the template for this instantiated element")
    name: str = Field(..., title="Name", description="name of the element")
    description: Optional[str] = Field(
        title="Description", description="short description of the element"
    )
    class_of_supply: Optional[ClassOfSupply] = Field(
        title="Class of Supply", description="class of supply number"
    )
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
    states: Optional[List[State]] = Field(title="States", description="list of states the element may possess")
    current_state_index: Optional[SafeInt] = Field(title="Current State", description="the current state of the element")

    class Config:
        """
        Configuration inner class forbidding additional fields
        """

        extra = Extra.forbid


class InstCargoCarrier(InstElement, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.
    
    :param SafeNonNegFloat max_cargo_mass: cargo capacity constraint (kg) (optional)
    :param SafeNonNegFloat max_cargo_volume: cargo capacity constraint (m^3) (optional)

    """
    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        title="Max Cargo Mass", description="cargo capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        title="Maximum Cargo Volume", description="cargo capacity constraint (m^3)",
    )



class InstResourceContainer(InstCargoCarrier):
    """
    An element representing a container for resources.

    :param [ResourceAmount | GenericResourceAmount] contents: list of resource quantities moved into container during spatial simulation (optional)
    """

    contents: Optional[List[Union[GenericResourceAmount, ResourceAmount]]] = Field(title="Resource Amount", description="list of resource quantities moved into container during spatial simulation")

class InstElementCarrier(InstCargoCarrier):
    """
    An element which can carry other elements.

    :param Environment cargo_environment: the cargo's environment - if unpressurized, cannot add pressurized elements as cargo (optional)
    :param [InstElementUUID] contents: list of instantiated elements moved into carrier during spatial simulation
    """

    cargo_environment: Optional[Environment] = Field(
        title="Cargo Environment",
        description="the cargo's environment — if "
        "unpressurized, "
        "cannot add pressurized elements as "
        "cargo",
    ),
    contents: List[InstElementUUID] = Field([], title="Contents", description="list of elements moved into carrier during spatial simulation")



class InstAgent(InstElement, ABC):
    """
    An abstract base class representing a generic Agent element.
    
    :param active_time_fraction: the fraction of the day that an agent is active (available) (optional)
    :type active_time_fraction: float from 0 to 1

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
        
    :param SafeNonNegInt max_crew: crew capacity constraint

    """
    max_crew: Optional[SafeNonNegInt] = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class InstPropulsiveVehicle(InstVehicle):
    """
    An element representing a vehicle with its own propulsion.
    
    :param SafeNonNegFloat isp: specific impulse (s) (optional)
    :param SafeNonNegFloat max_fuel: maximum fuel (units) (optional)
    :param ResourceAmount propellant: UUID and amount of propellant used by propulsive vehicle (optional)
    """

    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="maximum fuel (units)"
    )
    #TODO: fix this
    propellant: Optional[ResourceAmountRate] = Field(title="Propellant", description="UUID of propellant resource and rate")
    isp: Optional[SafeNonNegFloat] = Field(title="Specific Impulse", description="specific impulse (s)"
    )


class InstSurfaceVehicle(InstVehicle):
    """
    An element representing a surface vehicle.

    :param SafeNonNegFloat max_speed: maximum speed (kph) (optional)
    :param SafeNonNegFloat max_fule: maximum fuel (units) (optional)
    :param propellant ResourceAmountRate: UUID and rate of propellant used by propulsive vehicle

    """

    max_speed: Optional[SafeNonNegFloat] = Field(
        title="Maximum Speed", description="maximum speed (kph)"
    )
    max_fuel: Optional[SafeNonNegFloat] = Field(
        title="Maximum Fuel", description="maximum fuel (units)"
    )
    #TODO: could this also be GenericResourceAmount?
    propellant: Optional[ResourceAmountRate] = Field(title="Propellant", description="UUID of propellant resource and rate")


AllInstElements = Union[
    InstElement,
    InstResourceContainer,
    InstElementCarrier,
    InstHumanAgent,
    InstRoboticAgent,
    InstPropulsiveVehicle,
    InstSurfaceVehicle,
]
