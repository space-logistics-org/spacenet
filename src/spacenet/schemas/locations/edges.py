"""
Edges define valid paths (trajectories) between nodes.
"""

from abc import ABC
from datetime import timedelta
from enum import Enum
from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field
from typing_extensions import Literal

from .burn import Burn
from .location import Location, LocationUUID


class EdgeType(str, Enum):
    """
    An enumeration of edge types.
    """

    SURFACE = "Surface Edge"
    SPACE = "Space Edge"
    FLIGHT = "Flight Edge"


class EdgeUUID(LocationUUID):
    """
    Edge referenced by unique identifier.
    """


class Edge(Location, ABC):
    """
    Abstract base class for an edge.
    """

    type: EdgeType = Field(
        ...,
        title="Type",
        description="Edge type",
    )
    origin: UUID = Field(
        ..., title="Origin Node", description="Origin node unique identifier"
    )
    destination: UUID = Field(
        ...,
        title="Destination Node",
        description="Destination node unique identifier",
    )
    cost_per_transport: Optional[float] = Field(
        None,
        title="Cost per Transport",
        description="Cost (millions of US dollars) of each transport along the "
        "edge, e.g., a launch service or ground operations",
        ge=0,
    )
    min_departure_interval: Optional[float] = Field(
        None,
        title="Minimum Departure Interval",
        description="Shortest time (days) between transports departing along "
        "the edge, e.g., the launch cadence of a pad",
        ge=0,
    )


class SurfaceEdge(Edge):
    """
    Surface trajectory between two surface nodes.
    """

    type: Literal[EdgeType.SURFACE] = Field(
        EdgeType.SURFACE,
        title="Type",
        description="Edge type",
    )
    distance: float = Field(
        ..., title="Distance", description="Distance (m) of surface trajectory", ge=0
    )


class SpaceEdge(Edge):
    """
    An in-space trajectory between two nodes using a propulsive burn sequence.
    """

    type: Literal[EdgeType.SPACE] = Field(
        EdgeType.SPACE,
        title="Type",
        description="Edge type",
    )
    duration: timedelta = Field(
        ..., title="Duration", description="Duration of space edge"
    )
    burns: List[Burn] = Field(
        [],
        title="Burns",
        description="List of propulsive burns required to traverse the edge",
    )


class FlightEdge(Edge):
    """
    A trajectory between two nodes that is known to be feasible for a given
    cargo (mass) and crew capacity under a specified flight architecture.
    """

    type: Literal[EdgeType.FLIGHT] = Field(
        EdgeType.FLIGHT,
        title="Type",
        description="Edge type",
    )
    duration: timedelta = Field(
        ..., title="duration", description="Duration of traversal between nodes"
    )
    max_crew: int = Field(
        ...,
        title="Max Crew",
        description="Maximum number of crew to be transported",
        ge=0,
    )
    max_cargo: float = Field(
        ..., title="Max Cargo", description="Maximum cargo (kg) to be transported", ge=0
    )


AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
