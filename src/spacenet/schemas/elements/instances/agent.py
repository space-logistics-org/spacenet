"""Defines object schemas for instantiated agent elements."""

from abc import ABC
from typing import Optional

from pydantic import Field
from typing_extensions import Literal

from ..element import ElementType
from .element import InstElement


class InstAgent(InstElement, ABC):
    """
    Abstract base class for an agent.

    """

    active_time_fraction: Optional[float] = Field(
        title="Active Time Fraction",
        description="fraction time an agent is available (0 to 1 inclusive)",
        ge=0,
        le=1,
    )


class InstHumanAgent(InstAgent):
    """
    Instantiated human agent, i.e., a crew member.
    """

    type: Literal[ElementType.HUMAN_AGENT] = Field(
        ElementType.HUMAN_AGENT, description="Element type"
    )


class InstRoboticAgent(InstAgent):
    """
    Instantiated robotic agent.
    """

    type: Literal[ElementType.ROBOTIC_AGENT] = Field(
        ElementType.ROBOTIC_AGENT, description="Element type"
    )
