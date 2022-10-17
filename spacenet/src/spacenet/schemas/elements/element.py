"""Defines object schemas for generic element templates."""

from abc import ABC
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID

from pydantic import Field
from typing_extensions import Literal

from .state import State
from .part import Part

from ..utils import (
    SafeInt,
    SafeNonNegFloat,
    ImmutableBaseModel,
    ClassOfSupply,
    Environment,
)


class ElementType(str, Enum):
    """
    Enumeration of element types
    """

    ELEMENT = "Element"
    RESOURCE_CONTAINER = "Resource Container"
    ELEMENT_CARRIER = "Element Carrier"
    HUMAN_AGENT = "Human Agent"
    ROBOTIC_AGENT = "Robotic Agent"
    PROPULSIVE_VEHICLE = "Propulsive Vehicle"
    SURFACE_VEHICLE = "Surface Vehicle"


class ElementUUID(ImmutableBaseModel):
    """
    Element referenced by unique identifier.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Element(ElementUUID):
    """
    Generic entity that persists over time.

    :param str name: element name
    :param ElementType type: element type
    :param str description: short description (optional)
    :param ClassOfSupply class_of_supply: class of supply
    :param Environment environment: required stowage environment
    :param SafeNonNegFloat accommodation_mass: amount of COS 5 (kg) required for stowage
    :param SafeNonNegFloat mass: mass (kg)
    :param SafeNonNegFloat volume: volume (m^3)
    :param [State] states: list of operational states
    :param SafeInt current_state_index: index of the current operational state
    """

    name: str = Field(..., title="Name", description="Element name")
    type: Literal[ElementType.ELEMENT] = Field(
        ElementType.ELEMENT, description="Element type"
    )
    description: Optional[str] = Field(
        None, title="Description", description="Short description (optional)"
    )
    class_of_supply: ClassOfSupply = Field(
        ..., title="Class of Supply", description="Class of supply"
    )
    environment: Environment = Field(
        ..., title="Environment", description="Required stowage environment"
    )
    accommodation_mass: SafeNonNegFloat = Field(
        ...,
        title="Accommodation Mass",
        description="Amount of COS 5 (kg) required for stowage.",
    )
    mass: SafeNonNegFloat = Field(..., title="Mass", description="Mass (kg)")
    volume: SafeNonNegFloat = Field(..., title="Volume", description="Volume (m^3)")
    states: List[State] = Field(
        [], title="States", description="List of operational states"
    )
    current_state_index: Optional[SafeInt] = Field(
        None,
        title="Current State",
        description="Index of the current operational state",
    )
    parts: List[Part] = Field(
        [], title="Parts", description="List of constituent parts"
    )
    icon: Optional[str] = Field(title="Icon")


class CargoCarrier(Element, ABC):
    """
    Abstract base class for a carrier of cargo, elements or resources.

    :param SafeNonNegFloat max_cargo_mass: cargo mass capacity constraint (kg)
    :param SafeNonNegFloat max_cargo_volume: cargo volume capacity constraint (m^3)
    :param Environment cargo_environment: cargo stowage environment
    """

    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        0, title="Max Cargo Mass", description="Cargo mass capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        0,
        title="Maximum Cargo Volume",
        description="Cargo volume capacity constraint (m^3)",
    )
    cargo_environment: Environment = Field(
        ..., title="Cargo Environment", description="Cargo stowage environment",
    )
