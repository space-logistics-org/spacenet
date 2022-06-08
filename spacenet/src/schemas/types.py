"""
This module defines commonly useful types used by various schema.
"""
from math import inf

from pydantic import confloat, conint

from .constants import SQLITE_MAX_INT, SQLITE_MIN_INT

__all__ = [
    "SafeInt",
    "SafePosInt",
    "SafeNonNegInt",
    "SafeFloat",
    "SafePosFloat",
    "SafeNonNegFloat",
]
# Safe here refers to the ability to serialize types for transmission and store them in the
# database.
SafeInt = conint(ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT, strict=True)
SafePosInt = conint(gt=0, le=SQLITE_MAX_INT, strict=True)
SafeNonNegInt = conint(ge=0, le=SQLITE_MAX_INT, strict=True)
SafeFloat = confloat(gt=-inf, lt=inf)
SafePosFloat = confloat(gt=0, lt=inf)
SafeNonNegFloat = confloat(ge=0, lt=inf)
