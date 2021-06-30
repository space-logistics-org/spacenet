from math import inf

from typing_extensions import Literal

from pydantic import BaseModel, Field, confloat, conint
from enum import Enum

__all__ = ["Edge", "EdgeType", "FlightEdge", "SpaceEdge", "SurfaceEdge"]

from spacenet.constants import SQLITE_MAX_INT, SQLITE_MIN_INT


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
    origin_id: conint(strict=True, ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT) = Field(
        ..., title="Origin ID", description="ID of the origin node"
    )
    destination_id: conint(strict=True, ge=SQLITE_MIN_INT, le=SQLITE_MAX_INT) = Field(
        ..., title="Destination ID", description="ID of the destination node",
    )


class SurfaceEdge(Edge):
    """
    An edge between two surface nodes.
    """

    type: Literal[EdgeType.Surface] = Field(
        title="Type", description="Type of edge",
    )
    distance: confloat(ge=0, lt=inf) = Field(
        ..., title="Distance", description="Distance of surface edge"
    )


class SpaceEdge(Edge):
    """
    An edge between two nodes using a specified list of propulsive burns.
    """

    type: Literal[EdgeType.Space] = Field(
        title="Type", description="Type of edge",
    )
    duration: confloat(ge=0, lt=inf) = Field(
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
    duration: confloat(ge=0, lt=inf) = Field(
        ..., title="duration", description="Duration of flight edge"
    )
    max_crew: conint(strict=True, ge=0, le=SQLITE_MAX_INT) = Field(
        ..., title="Max Crew", description="Crew capacity for flight",
    )
    max_cargo: confloat(ge=0, lt=inf) = Field(
        ..., title="Max Cargo", description="Cargo capacity for flight"
    )
