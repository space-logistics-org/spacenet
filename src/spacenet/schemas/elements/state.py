"""
Element states define operational conditions.
"""

from typing import List, Optional
from enum import Enum
from uuid import uuid4, UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..demand_models import InstElementDemandModel


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
    demand_models: List[InstElementDemandModel] = Field(
        [], title="Demand Models", description="List of instantiated demand models"
    )
