"""
This module defines schemas for network edges.
"""
from enum import Enum
from typing import Union
from uuid import uuid4, UUID

from pydantic import BaseModel, Field
from typing_extensions import Literal

from .node import NodeUUID
from spacenet.schemas.mixins import ImmutableBaseModel
from spacenet.schemas.types import SafeInt, SafeNonNegFloat, SafeNonNegInt

__all__ = [
    "EdgeUUID",
    "Edge",
    "EdgeType",
    "FlightEdge",
    "SpaceEdge",
    "SurfaceEdge",
    "AllEdges",
]


class EdgeType(str, Enum):
    """
    An enumeration for the types of edges.
    """

    Surface = "SurfaceEdge"
    Space = "SpaceEdge"
    Flight = "FlightEdge"


class EdgeUUID(ImmutableBaseModel):
    """
    A base class which defines an edge by its UUID only.
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for edge")


class Edge(EdgeUUID):
    """
    Second base class for all edges.
    """

    name: str = Field(
        ..., title="Name", description="name of the edge",
    )
    description: str = Field(
        ..., title="Description", description="short description of the edge",
    )
    origin_id: NodeUUID = Field(
        ..., title="Origin Node", description="UUID of the origin node"
    )
    destination_id: NodeUUID = Field(
        ..., title="Destination Node", description="UUID of the destination node",
    )


class SurfaceEdge(Edge):
    """
    An edge between two surface nodes.
    """

    type: Literal[EdgeType.Surface] = Field(
        title="Type", description="Type of edge",
    )
    distance: SafeNonNegFloat = Field(
        ..., title="Distance", description="Distance of surface edge"
    )


class SpaceEdge(Edge):
    """
    An edge between two nodes using a specified list of propulsive burns.
    """

    type: Literal[EdgeType.Space] = Field(
        title="Type", description="Type of edge",
    )
    duration: SafeNonNegFloat = Field(
        ..., title="Duration", description="Duration of space edge"
    )
    delta_v: SafeNonNegFloat = Field(
        ...,
        title="Delta-V",
        description="Acceleration required to traverse this edge in m/s",
    )


class FlightEdge(Edge):
    """
    An edge between two nodes using flight architectures that are known to close
    with a given cargo and crew capacity.
    """

    type: Literal[EdgeType.Flight] = Field(
        ..., title="Type", description="Type of edge",
    )
    duration: SafeNonNegFloat = Field(
        ..., title="duration", description="Duration of flight edge"
    )
    max_crew: SafeNonNegInt = Field(
        ..., title="Max Crew", description="Crew capacity for flight",
    )
    max_cargo: SafeNonNegFloat = Field(
        ..., title="Max Cargo", description="Cargo capacity for flight"
    )

AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
