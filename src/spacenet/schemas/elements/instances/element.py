"""Defines object schemas for instantiated generic elements."""

from abc import ABC
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from ...resources import ClassOfSupply, Environment
from ..element import ElementType
from ..state import State


class InstElementUUID(CamelModel):
    """
    Instantiated element referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class InstElement(InstElementUUID):
    """
    Generic element instance.
    """

    type: Literal[ElementType.ELEMENT] = Field(
        ElementType.ELEMENT, description="element type"
    )
    template_id: UUID = Field(..., description="Element template unique identifier")
    name: str = Field(..., title="Name", description="Element name")
    description: Optional[str] = Field(
        None, title="Description", description="Short description (optional)"
    )
    class_of_supply: Optional[ClassOfSupply] = Field(
        None, title="Class of Supply", description="Class of supply"
    )
    environment: Optional[Environment] = Field(
        None, title="Environment", description="Required stowage environment"
    )
    accommodation_mass: Optional[float] = Field(
        None, title="Accommodation Mass",
        description="Amount of COS 5 (kg) required for stowage",
        ge=0,
    )
    mass: Optional[float] = Field(None, title="Mass", description="Mass (kg)", ge=0)
    volume: Optional[float] = Field(None, title="Volume", description="Volume (m^3)", ge=0)
    states: Optional[List[State]] = Field(
        None, title="States", description="List of operational states"
    )
    current_state_index: Optional[int] = Field(
        None, title="Current State",
        description="Index of the current operational state",
        ge=-1,
    )
    parts: Optional[List[UUID]] = Field(
        None, title="Parts", description="List of constituent parts"
    )
    icon: Optional[str] = Field(None, title="Icon")


class InstCargoCarrier(InstElement, ABC):
    """
    Abstract base class for a carrier of cargo, elements or resources.
    """

    max_cargo_mass: Optional[float] = Field(
        None, title="Max Cargo Mass", description="Cargo mass capacity constraint (kg)", ge=0
    )
    max_cargo_volume: Optional[float] = Field(
        None, title="Maximum Cargo Volume",
        description="Cargo volume capacity constraint (m^3)",
        ge=0,
    )
    cargo_environment: Optional[Environment] = Field(
        None, title="Cargo Environment",
        description="Cargo stowage environment",
    )
