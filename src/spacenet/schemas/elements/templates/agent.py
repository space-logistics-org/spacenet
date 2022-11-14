"""Defines object schemas for agent element templates."""

from abc import ABC

from pydantic import Field
from typing_extensions import Literal

from ..element import ElementType
from .element import Element


class Agent(Element, ABC):
    """
    Abstract base class for an agent.
    """

    active_time_fraction: float = Field(
        ...,
        title="Active Time Fraction",
        description="fraction time an agent is available (0 to 1 inclusive)",
        ge=0,
        le=1,
    )


class HumanAgent(Agent):
    """
    Human agent, i.e., a crew member.
    """

    type: Literal[ElementType.HUMAN_AGENT] = Field(
        ElementType.HUMAN_AGENT, description="Element type"
    )


class RoboticAgent(Agent):
    """
    Robotic agent.
    """

    type: Literal[ElementType.ROBOTIC_AGENT] = Field(
        ElementType.ROBOTIC_AGENT, description="Element type"
    )
