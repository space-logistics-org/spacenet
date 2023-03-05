"""Defines object schemas for generic element templates."""

from abc import ABC
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from ...resources import ClassOfSupply, Environment
from ..element import ElementType
from ..part import Part
from ..state import State


class ElementUUID(CamelModel):
    """
    Element referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Element(ElementUUID):
    """
    Generic entity that persists over time.
    """

    name: str = Field(..., title="Name", description="Element name")
    type: Literal[ElementType.ELEMENT] = Field(
        ElementType.ELEMENT, description="Element type"
    )
    description: Optional[str] = Field(
        None, title="Description", description="Short description (optional)"
    )
    class_of_supply: ClassOfSupply = Field(
        ClassOfSupply.COS_0, title="Class of Supply", description="Class of supply"
    )
    environment: Environment = Field(
        Environment.UNPRESSURIZED, title="Environment", description="Required stowage environment"
    )
    accommodation_mass: float = Field(
        0,
        title="Accommodation Mass",
        description="Amount of COS 5 (kg) required for stowage.",
        ge=0,
    )
    mass: float = Field(0, title="Mass", description="Mass (kg)", ge=0)
    volume: float = Field(0, title="Volume", description="Volume (m^3)", ge=0)
    states: List[State] = Field(
        [], title="States", description="List of operational states"
    )
    current_state_index: Optional[int] = Field(
        None,
        title="Current State",
        description="Index of the current operational state",
        ge=-1,
    )
    parts: List[Part] = Field(
        [], title="Parts", description="List of constituent parts"
    )
    icon: Optional[str] = Field(title="Icon")


class CargoCarrier(Element, ABC):
    """
    Abstract base class for a carrier of cargo, elements or resources.
    """

    max_cargo_mass: Optional[float] = Field(
        0,
        title="Max Cargo Mass",
        description="Cargo mass capacity constraint (kg)",
        ge=0,
    )
    max_cargo_volume: Optional[float] = Field(
        0,
        title="Maximum Cargo Volume",
        description="Cargo volume capacity constraint (m^3)",
        ge=0,
    )
    cargo_environment: Environment = Field(
        Environment.UNPRESSURIZED,
        title="Cargo Environment",
        description="Cargo stowage environment",
    )
