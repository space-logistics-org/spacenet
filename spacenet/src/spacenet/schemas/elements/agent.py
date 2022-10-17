"""Defines object schemas for agent element templates."""

from abc import ABC

from pydantic import Field, confloat
from typing_extensions import Literal

from .element import Element, ElementType


class Agent(Element, ABC):
    """
    Abstract base class for an agent.

    :param active_time_fraction float: fraction time an agent is available (0 to 1 inclusive)
    """

    active_time_fraction: confloat(ge=0, le=1) = Field(
        ...,
        title="Active Time Fraction",
        description="fraction time an agent is available (0 to 1 inclusive)",
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
