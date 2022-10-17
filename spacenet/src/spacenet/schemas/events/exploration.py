"""
Defines object schemas for exploration events.
"""
from datetime import timedelta
from typing import List, Union
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType

from ..resources import ResourceAmount, GenericResourceAmount
from ..utils import SafeNonNegFloat, SafeInt


class ElementState(CamelModel):
    """
    Specification of an element state.

    :param UUID element: unique identifier of element
    :param SafeInt state_index: index of the referenced state
    """

    element: UUID = Field(
        ..., title="element", description="Unique identifier of element"
    )
    state_index: SafeInt = Field(
        ...,
        title="State Index",
        description="Index of the referenced state (-1 if none)",
    )


class CrewedEVA(Event):
    """
    Event for a crewed extravehicular activity.

    :param timedelta eva_duration: duration of the extra-vehiclular activity
    :param UUID vehicle: unique identifier of the crew habitat from which crew will egress and ingress
    :param List[ElementState] element_states: list of reconfiguration states for each participating element
    :param [ResourceAmount | GenericResourceAmount] additional_demands: list of additional resource amounts to be consumed
    """

    type: Literal[EventType.CREWED_EVA] = Field(
        EventType.CREWED_EVA, title="Type", description="Event type",
    )
    eva_duration: timedelta = Field(
        ...,
        title="EVA Duration",
        description="Duration of the extra-vehicular activity",
    )
    vehicle: UUID = Field(
        ...,
        title="Crew Vehicle",
        description="Unique identifier of the crew habitat from which crew will egress and ingress",
    )
    element_states: List[ElementState] = Field(
        ...,
        description="List of reconfiguration states for each participating element",
    )
    additional_demands: List[Union[ResourceAmount | GenericResourceAmount]] = Field(
        ...,
        title="Additional Demands",
        description="List of additional resource amounts to be consumed",
    )


class CrewedExploration(Event):
    """
    Event for a crewed exploration period that consists of regularly-scheduled
    extra-vehicular activities.

    :param timedelta eva_duration: duration of the extra-vehiclular activity
    :param timedelta duration: duration of the exploration
    :param tUUID vehicle: unique identifier of the crew habitat from which crew will egress and ingress
    :param SafeNonNegFloat eva_per_week: number of extra-vehiclular activitys to be performed per week
    :param List[ElementState] element_states: list of reconfiguration states for each participating element
    :param [UUID] additional_demands: list of additional resource amounts to be consumed
    """

    type: Literal[EventType.CREWED_EXPLORATION] = Field(
        EventType.CREWED_EXPLORATION, title="Type", description="Event type",
    )
    eva_duration: timedelta = Field(
        ...,
        title="EVA Duration",
        description="Duration of the extra-vehicular activity",
    )
    duration: timedelta = Field(
        ..., title="Duration", description="Duration of the exploration"
    )
    vehicle: UUID = Field(
        ...,
        title="Crew Vehicle",
        description="Unique identifier of the crew habitat from which crew will egress and ingress",
    )
    eva_per_week: SafeNonNegFloat = Field(
        ...,
        title="EVAs per week",
        description="Number of extra-vehiclular activitys to be performed per week",
    )
    element_states: List[ElementState] = Field(
        ...,
        description="List of reconfiguration states for each participating element",
    )
    additional_demands: List[UUID] = Field(
        [],
        title="Additional Demands",
        description="List of additional resource amounts to be consumed",
    )
