"""Defines object schemas for element operational states."""

from typing import List, Optional
from enum import Enum
from uuid import uuid4, UUID

from pydantic import Field

from ..utils import ImmutableBaseModel
from ..demand_models import InstElementDemandModel


class StateType(str, Enum):
    """
    Enumeration of state types.
    """

    ACTIVE = "Active"
    QUIESCENT = "Quiescent"
    DORMANT = "Dormant"
    DECOMMISSIONED = "Decommissioned"


class StateUUID(ImmutableBaseModel):
    """
    State referenced by unique identifier.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class State(StateUUID):
    """
    An element's operational state.

    :param str name: state name
    :param str description: short description (optional)
    :param StateType type: state type
    :param [InstDemandModel] demand_models: list of instantiated demand models associated with this state
    """

    name: str = Field(..., description="State name")
    description: Optional[str] = Field(
        None, title="Description", description="Short description (optional)"
    )
    type: StateType = Field(..., description="State type")
    demand_models: List[InstElementDemandModel] = Field(
        [], title="Demand Models", description="List of instantiated demand models"
    )
