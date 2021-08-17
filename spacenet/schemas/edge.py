"""
This module defines schemas for network edges.
"""
from enum import Enum
from typing import Union
from uuid import UUID

from pydantic import BaseModel, Field
from typing_extensions import Literal

from spacenet.schemas.mixins import ImmutableBaseModel
from spacenet.schemas.types import SafeInt, SafeNonNegFloat, SafeNonNegInt

__all__ = [
    "Edge",
    "EdgeType",
    "FlightEdge",
    "SpaceEdge",
    "SurfaceEdge",
    "UUIDEdge",
    "UUIDFlightEdge",
    "UUIDSpaceEdge",
    "UUIDSurfaceEdge",
    "AllEdges",
    "AllUUIDEdges",
]


class EdgeType(str, Enum):
    """
    An enumeration for the types of edges.
    """

    Surface = "SurfaceEdge"
    Space = "SpaceEdge"
    Flight = "FlightEdge"


class UUID_IDs(ImmutableBaseModel):
    """
    A mixin schema which uses UUIDs for origin and destination IDs.
    """

    origin_id: UUID = Field(..., title="Origin ID", description="ID of the origin node")

    destination_id: UUID = Field(
        ..., title="Destination ID", description="ID of the destination node",
    )


class Edge(BaseModel):
    """
    Base class for all edges.
    """

    name: str = Field(
        ..., title="Name", description="name of the edge",
    )
    description: str = Field(
        ..., title="Description", description="short description of the edge",
    )
    origin_id: SafeInt = Field(
        ..., title="Origin ID", description="ID of the origin node"
    )
    destination_id: SafeInt = Field(
        ..., title="Destination ID", description="ID of the destination node",
    )


class UUIDEdge(UUID_IDs, Edge):
    """
    Base class for edges using UUIDs for origin and destination IDs.
    """

    # This ordering matters, reverse it and the types of ID fields are wrong
    pass


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


class UUIDSurfaceEdge(UUID_IDs, SurfaceEdge):
    """
    An edge between two surface nodes, using UUIDs for origin and destination IDs.
    """

    pass


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


class UUIDSpaceEdge(UUID_IDs, SpaceEdge):
    """
    An edge between two nodes using a specified list of propulsive burns,
    using UUIDs for origin and destination IDs.
    """

    pass


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


class UUIDFlightEdge(UUID_IDs, FlightEdge):
    """
    An edge between two nodes using flight architectures that are known to close
    with a given cargo and crew capacity, using UUIDs for origin and destination IDs.
    """

    pass


AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
AllUUIDEdges = Union[UUIDFlightEdge, UUIDSpaceEdge, UUIDSurfaceEdge]
