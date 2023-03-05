"""Defines object schemas for stowage environment."""

from enum import Enum


class Environment(str, Enum):
    """
    Enumeration of stowage environments.
    """

    PRESSURIZED = "Pressurized"
    UNPRESSURIZED = "Unpressurized"
