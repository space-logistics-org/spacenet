"""Defines types for safe serialization to databases."""

from math import inf

from pydantic import confloat, conint

SQLITE_MIN_INT = -1 * 2 ** 63
SQLITE_MAX_INT = 2 ** 63 - 1

__all__ = [
    "SafeInt",
    "SafePosInt",
    "SafeNonNegInt",
    "SafeFloat",
    "SafePosFloat",
    "SafeNonNegFloat",
]

SafeInt = conint(ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT, strict=True)
SafePosInt = conint(gt=0, le=SQLITE_MAX_INT, strict=True)
SafeNonNegInt = conint(ge=0, le=SQLITE_MAX_INT, strict=True)
SafeFloat = confloat(gt=-inf, lt=inf)
SafePosFloat = confloat(gt=0, lt=inf)
SafeNonNegFloat = confloat(ge=0, lt=inf)
