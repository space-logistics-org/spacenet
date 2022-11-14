"""Defines object schemas for demand models."""

from enum import Enum


class DemandModelType(str, Enum):
    """
    Enumeration of demand model types.
    """

    CREW_CONSUMABLES = "Crew Consumables"
    TIMED_IMPULSE = "Timed Impulse"
    RATED = "Rated"
    SPARING_BY_MASS = "Sparing By Mass"
