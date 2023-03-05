"""
This module defines a schema for specifying flight transport events, representing cases where
a vehicle is known to be able to traverse the given edge.
"""
from abc import ABC
from typing import List
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field
from typing_extensions import Literal

from .event import Event, EventType
from .burn import BurnStageItem


class TransportEvent(Event, ABC):
    """
    Abstract base class an event that transports instantiated elements along edges.
    """

    edge: UUID = Field(
        ...,
        description="Edge (by unique identifier) along which this transport traverses",
    )
    elements: List[UUID] = Field(
        ...,
        title="List of Elements",
        description="List of instantiated elements (by unique identifier) to transport",
    )


class FlightTransport(TransportEvent):
    """
    Event that transports instantiated elements along a flight edge.
    """

    type: Literal[EventType.FLIGHT_TRANSPORT] = Field(
        EventType.FLIGHT_TRANSPORT,
        title="Type",
        description="Event type",
    )


class SurfaceTransport(TransportEvent):
    """
    Event that transports instantiated elements along a surface edge.
    """

    type: Literal[EventType.SURFACE_TRANSPORT] = Field(
        EventType.SURFACE_TRANSPORT,
        title="Type",
        description="Event type",
    )


class BurnStageSequence(CamelModel):
    """
    A sequence of burn/stage events.
    """

    burn: UUID = Field(..., title="Burn", description="UUID of burn")
    actions: List[BurnStageItem] = Field(
        ..., description="List of the burns and stages to be performed in the event"
    )


class SpaceTransport(TransportEvent):
    """
    Event that transports instantiated elements along a space edge.
    """

    type: Literal[EventType.SPACE_TRANSPORT] = Field(
        EventType.SPACE_TRANSPORT,
        title="Type",
        description="Event type",
    )
    burn_stage_sequence: List[BurnStageSequence] = Field(
        ...,
        title="Burn Sequence",
        description="List of burn-stage sequences to perform",
    )
