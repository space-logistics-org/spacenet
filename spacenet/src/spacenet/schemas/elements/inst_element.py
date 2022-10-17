"""Defines object schemas for instantiated generic elements."""

from abc import ABC
from typing import List, Optional
from uuid import uuid4, UUID

from pydantic import Field
from typing_extensions import Literal

from .state import State
from .element import ElementType

from ..utils import (
    SafeInt,
    SafeNonNegFloat,
    ImmutableBaseModel,
    ClassOfSupply,
    Environment,
)


class InstElementUUID(ImmutableBaseModel):
    """
    Instantiated element referenced by unique identifier.

    :param UUID id: unique identifier

    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class InstElement(InstElementUUID):
    """
    Generic element instance.

    :param Element type: element type
    :param UUID template_id: element template unique identifier
    :param str name: instantiated element name
    :param str description: short description (optional)
    :param ClassOfSupply class_of_supply: class of supply (optional)
    :param Environment environment: required stowage environment (optional)
    :param SafeNonNegFloat accommodation_mass: amount of COS 5 (kg) required for stowage (optional)
    :param SafeNonNegFloat mass: mass (kg, optional)
    :param SafeNonNegFloat volume: volume (m^3, optional)
    :param List[State] states: list of operational states (optional)
    :param SafeInt current_state_index: index of the current operational state (optional)
    """

    type: Literal[ElementType.ELEMENT] = Field(
        ElementType.ELEMENT, description="element type"
    )
    template_id: UUID = Field(..., description="Element template unique identifier")
    name: str = Field(..., title="Name", description="Element name")
    description: Optional[str] = Field(
        title="Description", description="Short description (optional)"
    )
    class_of_supply: Optional[ClassOfSupply] = Field(
        title="Class of Supply", description="Class of supply"
    )
    environment: Optional[Environment] = Field(
        title="Environment", description="Required stowage environment"
    )
    accommodation_mass: Optional[SafeNonNegFloat] = Field(
        title="Accommodation Mass",
        description="Amount of COS 5 (kg) required for stowage",
    )
    mass: Optional[SafeNonNegFloat] = Field(title="Mass", description="Mass (kg)")
    volume: Optional[SafeNonNegFloat] = Field(
        title="Volume", description="Volume (m^3)"
    )
    states: Optional[List[State]] = Field(
        title="States", description="List of operational states"
    )
    current_state_index: Optional[SafeInt] = Field(
        title="Current State", description="Index of the current operational state"
    )
    parts: Optional[List[UUID]] = Field(
        title="Parts", description="List of constituent parts"
    )
    icon: Optional[str] = Field(title="Icon")


class InstCargoCarrier(InstElement, ABC):
    """
    Abstract base class for a carrier of cargo, elements or resources.

    :param SafeNonNegFloat max_cargo_mass: cargo mass capacity constraint (kg, optional)
    :param SafeNonNegFloat max_cargo_volume: cargo volume capacity constraint (m^3, optional)
    :param Environment cargo_environment: cargo stowage environment (optional)
    """

    max_cargo_mass: Optional[SafeNonNegFloat] = Field(
        title="Max Cargo Mass", description="Cargo mass capacity constraint (kg)"
    )
    max_cargo_volume: Optional[SafeNonNegFloat] = Field(
        title="Maximum Cargo Volume",
        description="Cargo volume capacity constraint (m^3)",
    )
    cargo_environment: Optional[Environment] = Field(
        title="Cargo Environment", description="Cargo stowage environment",
    )
