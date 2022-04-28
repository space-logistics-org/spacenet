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
from .element import ElementKind, ElementUUID
from .resource import ResourceAmount
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
    "InstElementKind",
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
    :param str name: name of the element (optional)
    :param str description: short description of the element (optional)
    :param ClassOfSupply class_of_supply: class of supply number (optional)
    :param Environment environment: the element's environment (optional)
    :param NonNegFloat accommodation_mass: the amount of additional COS5 required to pack the element inside a carrier (optional)
    :param NonNegFloat mass: mass in kg (optional)
    :param NonNegFloat volume: volume in cubic meters (optional)
    :param StateUUID current_state: field describing the current state of the element. Set to initial state during creation. (optional)
    """
    template_id: ElementUUID = Field(..., description="UUID of the template for this instantiated element")
    name: Optional[str] = Field(title="Name", description="name of the element")
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
    current_state: Optional[StateUUID] = Field(None, title="Current State", description="the current state of the element")

    class Config:
        """
        Configuration inner class forbidding additional fields
        """

        extra = Extra.forbid


class InstCargoCarrier(InstElement, ABC):
    """
    Abstract base class representing a carrier of some sort of cargo, elements or resources.
    
    :param NonNegFloat max_cargo_mass: cargo capacity constraint (kg) (optional)
    :param max_cargo_volume: cargo capacity constraint (m^3) (optional)
    :param [InstElementUUID | ResourceUUID] contents: list of elements or resources moved into carrier during spatial simulation (optional)

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

    :param [ResourceAmount] contents: list of resource quantities moved into container during spatial simulation
    """

    contents: List[ResourceAmount] = Field([], title="Resource Amount", description="list of resource quantities moved into container during spatial simulation")

class InstElementCarrier(InstCargoCarrier):
    """
    An element which can carry other elements.

    :param Environment cargo_environment: the cargo's environment - if unpressurized, cannot add pressurized elements as cargo (optional)
    :param [InstElementUUID] contents: list of elements moved into carrier during spatial simulation
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
        
    :param NonNegInt max_crew: crew capacity constraint

    """
    max_crew: Optional[SafeNonNegInt] = Field(
        ..., title="Maximum Crew Count", description="crew capacity constraint"
    )


class InstPropulsiveVehicle(InstVehicle):
    """
    An element representing a vehicle with its own propulsion.
    
    :param NonNegFloat isp: "specific impulse (s) (optional)
    :param NonNegFloat max_fuel: maximum fuel (units) (optional)

    """

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

    :param NonNegFloat max_speed: maximum speed (kph) (optional)
    :param NonNegFloat max_fule: maximum fuel (units) (optional)

    """

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
