"""
Defines object schemas for the electrical power and energy storage of elements.
"""

from enum import Enum
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import Field


class PowerGenerationType(str, Enum):
    """
    Enumeration of the types of power generation.
    """

    #: Generation independent of illumination (e.g., fission, radioisotope, fuel cell).
    CONSTANT = "Constant"
    #: Generation proportional to the illumination of the location (solar arrays).
    SOLAR = "Solar"


class EnergyStorage(CamelModel):
    """
    Electrical energy storage (e.g., batteries or regenerative fuel cells).
    """

    capacity: float = Field(
        ..., title="Capacity", description="Energy storage capacity (kWh)", ge=0
    )
    charge: Optional[float] = Field(
        None,
        title="Initial Charge",
        description="Initial stored energy (kWh) (default: the capacity)",
        ge=0,
    )
