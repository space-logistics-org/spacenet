"""
Propulsive burns define the change in velocity required to
transition between nodes using impulsive propulsion.
"""

from datetime import timedelta
from uuid import UUID, uuid4

from fastapi_camelcase import CamelModel
from pydantic import Field


class BurnUUID(CamelModel):
    """
    Propulsive burn referenced by unique identifier.
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Burn(BurnUUID):
    """
    Impulsive propulsive burn triggered at a designated time during a space
    transport to generate a target change in velocity (delta-V).
    """

    time: timedelta = Field(
        ..., description="Time relative to the start of the space transport"
    )
    delta_v: float = Field(
        ..., description="Change in velocity (m/s) to be achieved", ge=0
    )
