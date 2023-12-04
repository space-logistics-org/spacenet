"""
This module defines a schema for specifying flight transport events, representing cases where
a vehicle is known to be able to traverse the given edge.
"""
from abc import ABC
from typing import List, Optional
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


class FlightTransport(TransportEvent):
    """
    Event that transports instantiated elements along a flight edge.
    """

    type: Literal[EventType.FLIGHT_TRANSPORT] = Field(
        EventType.FLIGHT_TRANSPORT,
        title="Type",
        description="Event type",
    )
    elements: List[UUID] = Field(
        ...,
        title="List of Elements",
        description="List of instantiated elements (by unique identifier) to transport",
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
    vehicle: UUID = Field(
        ...,
        title="Surface Vehicle",
        description="Surface vehicle (by unique identifier) to transport",
    )
    transport_state: Optional[int] = Field(
        title="Transport State Index",
        description="Index of the transport state",
        ge=-1,
    )
    speed: float = Field(
        ..., title="Transport Speed", description="Transport speed (m/s)", gt=0
    )
    duty_cycle: float = Field(
        1,
        title="Duty Cycle",
        description="Fraction of the time the vehicle is moving at the transport speed",
        gt=0,
        le=1,
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
    elements: List[UUID] = Field(
        ...,
        title="List of Elements",
        description="List of instantiated elements (by unique identifier) to transport",
    )
    burn_stage_sequence: List[BurnStageSequence] = Field(
        ...,
        title="Burn Sequence",
        description="List of burn-stage sequences to perform",
    )
