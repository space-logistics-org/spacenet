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
from .mixins import ImmutableBaseModel
from .types import SafeInt, SafeNonNegFloat, SafeNonNegInt
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

    Surface = "Surface Edge"
    Space = "Space Edge"
    Flight = "Flight Edge"


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
    :param UUID origin: UUID of the origin node
    :param UUID destination: UUID of the destination node
    :param [UUID] contents: list of UUIDs of elements stored at this edge during the spatial simulation

    """
#TODO: elements stored in edge during simulation or in edge all along?
    name: str = Field(
        ..., title="Name", description="name of the edge",
    )
    description: str = Field(
        ..., title="Description", description="short description of the edge",
    )
    origin: UUID = Field(
        ..., title="Origin Node", description="UUID of the origin node"
    )
    destination: UUID = Field(
        ..., title="Destination Node", description="UUID of the destination node",
    )
    contents: List[UUID] = Field([], title="Contents", description="list of UUIDs of elements stored at this edge during the spatial simulation")



class SurfaceEdge(Edge):
    """
    An edge between two surface nodes.

    :param SurfaceEdge type: type of edge
    :param NonNegFloat distance: distance edge traverses
    """

    type: Literal[EdgeType.Surface] = Field(
        EdgeType.Surface, title="Type", description="Type of edge",
    )
    distance: SafeNonNegFloat = Field(
        ..., title="Distance", description="Distance edge traverses"
    )


class SpaceEdge(Edge):
    """
    An edge between two nodes using a specified list of propulsive burns.

    :param SpaceEdge type: the edge's type
    :param timedelta duration: duration of space edge
    :param [Burn] burns: list of propulsive burns that take place along this space edge
    """

    type: Literal[EdgeType.Space] = Field(
        EdgeType.Space, title="Type", description="Type of edge",
    )
    duration: timedelta = Field(
        ..., title="Duration", description="Duration of space edge"
    )
    burns: List[Burn] = Field(..., title="Burns", description="List of propulsive burns that take place along this space edge")


class FlightEdge(Edge):
    """
    An edge between two nodes using flight architectures that are known to close
    with a given cargo and crew capacity.

    :param FlightEdge type: the edge's type
    :param timedelta duration: duration of flight edge
    :param NonNegInt max_crew: crew capacity along the entire edge
    :param NonNegFloat max_cargo: cargo capacity along the entire edge
    """

    type: Literal[EdgeType.Flight] = Field(
        EdgeType.Flight, title="Type", description="Type of edge",
    )
    duration: timedelta = Field(
        ..., title="duration", description="Duration of flight edge"
    )
    max_crew: SafeNonNegInt = Field(
        ..., title="Max Crew", description="Crew capacity along the entire edge",
    )
    max_cargo: SafeNonNegFloat = Field(
        ..., title="Max Cargo", description="Cargo capacity along the entire edge"
    )

AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
