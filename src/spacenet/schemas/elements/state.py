"""
Element states define operational conditions.
"""

from typing import List, Optional
from enum import Enum
from uuid import uuid4, UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..demand_models import AllInstElementDemandModels
from .power import PowerGenerationType


class StateType(str, Enum):
    """
    Enumeration of state types.
    """

    ACTIVE = "Active"
    QUIESCENT = "Quiescent"
    DORMANT = "Dormant"
    DECOMMISSIONED = "Decommissioned"


class StateUUID(CamelModel):
    """
    State referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class State(StateUUID):
    """
    An element's operational state.
    """

    name: str = Field(..., description="State name")
    description: Optional[str] = Field(
        None, title="Description", description="Short description (optional)"
    )
    type: StateType = Field(..., description="State type")
    demand_models: List[AllInstElementDemandModels] = Field(
        [], title="Demand Models", description="List of instantiated demand models"
    )
    power_consumption: Optional[float] = Field(
        None,
        title="Power Consumption",
        description="Electrical power (kW) consumed in this state",
        ge=0,
    )
    power_generation: Optional[float] = Field(
        None,
        title="Power Generation",
        description="Electrical power (kW) generated in this state (when fully "
        "illuminated, for solar generation)",
        ge=0,
    )
    generation_type: Optional[PowerGenerationType] = Field(
        None,
        title="Generation Type",
        description="Type of power generation (default: constant)",
    )
