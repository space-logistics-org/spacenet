from typing_extensions import Literal

from pydantic import BaseModel, Field
from enum import Enum

__all__ = ["Edge", "EdgeType", "FlightEdge", "SpaceEdge", "SurfaceEdge"]

from spacenet.schemas.types import SafeInt, SafeNonNegFloat, SafeNonNegInt


class EdgeType(str, Enum):
    """
    An enumeration for the types of edges.
    """

    Surface = "SurfaceEdge"
    Space = "SpaceEdge"
    Flight = "FlightEdge"


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
