"""
This module defines schemas for network edges.
"""
from enum import Enum
from typing import Union, List
from uuid import uuid4, UUID
from datetime import timedelta

from pydantic import BaseModel, Field, NonNegativeFloat
from typing_extensions import Literal

from .node import NodeUUID
from spacenet.schemas.mixins import ImmutableBaseModel
from spacenet.schemas.types import SafeInt, SafeNonNegFloat, SafeNonNegInt
from .inst_element import InstElementUUID
from .burn import Burn

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

    Surface = "Surface"
    Space = "Space"
    Flight = "Flight"


class EdgeUUID(ImmutableBaseModel):
    """
    A base class which defines an edge by its UUID only.

    :param UUID id: unique identifier for edge
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for edge")


class Edge(EdgeUUID):
    """
    Second base class for all edges.

    :param str name: name of the edge
    :param str description: short description of the edge
    :param NodeUUID origin_id: UUID of the origin node
    :param NodeUUID destination_id: UUID of the destination node
    :param [InstElementUUID] contents: UUIDs of elements stored at this edge during the spatial simulation

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
    contents: List[InstElementUUID] = Field([], title="Contents", description="elements stored at this edge during the spatial simulation")



class SurfaceEdge(Edge):
    """
    An edge between two surface nodes.

    :param SurfaceEdge type: type of edge
    :param NonNegFloat distance: distance of surface edge
    """

    type: Literal[EdgeType.Surface] = Field(
        EdgeType.Surface, title="Type", description="Type of edge",
    )
    distance: SafeNonNegFloat = Field(
        ..., title="Distance", description="Distance of surface edge"
    )


class SpaceEdge(Edge):
    """
    An edge between two nodes using a specified list of propulsive burns.

    :param SpaceEdge type: the edge's type
    :param timedelta duration: duration of space edge
    :param NonNegFloat delta_v: acceleration required to traverse this edge in m/s
    """

    type: Literal[EdgeType.Space] = Field(
        EdgeType.Space, title="Type", description="Type of edge",
    )
    duration: timedelta = Field(
        ..., title="Duration", description="Duration of space edge"
    )
    delta_v: SafeNonNegFloat = Field(
        ...,
        title="Delta-V",
        description="Acceleration required to traverse this edge in m/s",
    ),
    burns: List[Burn] = Field(..., title="Burns", description="List of burns included in the space edge")


class FlightEdge(Edge):
    """
    An edge between two nodes using flight architectures that are known to close
    with a given cargo and crew capacity.

    :param FlightEdge type: the edge's type
    :param timedelta duration: duration of flight edge
    :param NonNegInt max_crew: crew capacity for flight
    :param NonNegFloat max_cargo: cargo capacity for flight
    """

    type: Literal[EdgeType.Flight] = Field(
        EdgeType.Flight, title="Type", description="Type of edge",
    )
    duration: timedelta = Field(
        ..., title="duration", description="Duration of flight edge"
    )
    max_crew: SafeNonNegInt = Field(
        ..., title="Max Crew", description="Crew capacity for flight",
    )
    max_cargo: SafeNonNegFloat = Field(
        ..., title="Max Cargo", description="Cargo capacity for flight"
    )

AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
