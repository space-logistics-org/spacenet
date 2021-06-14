from pydantic import BaseModel, Field
from enum import Enum


class EdgeType(str, Enum):
    """
    An enumeration for the types of edges.
    """
    Surface = "Surface"
    Space = "Space"
    Flight = "Flight"


class Edge(BaseModel):
    """
    Base class for all edges.
    """
    name: str = Field(
        ...,
        title="Name",
        description="name of the edge",
    )
    description: str = Field(
        ...,
        title="Description",
        description="short description of the edge",
    )
    origin_id: int = Field(
        ...,
        title="Origin ID",
        description="ID of the origin node"
    )
    destination_id: int = Field(
        ...,
        title="Destination ID",
        description="ID of the destination node"
    )


class SurfaceEdge(Edge):
    """
    An edge between two surface nodes.
    """
    type: EdgeType = Field(
        default=EdgeType.Surface,
        title="Type",
        description="Type of edge",
        const=True
    )
    distance: float = Field(
        ...,
        title="Distance",
        description="Distance of surface edge",
        ge=0
    )


class SpaceEdge(Edge):
    """
    An edge between two nodes using a specified list of propulsive burns.
    """
    type: EdgeType = Field(
        default=EdgeType.Space,
        title="Type",
        description="Type of edge",
        const=True
    )
    duration: float = Field(
        ...,
        title="Duration",
        description="Duration of space edge",
        ge=0
    )


class FlightEdge(Edge):
    """
    An edge between two nodes using flight architectures that are known to close
    with a given cargo and crew capacity.
    """
    type: EdgeType = Field(
        default=EdgeType.Flight,
        title="Type",
        description="Type of edge",
        const=True
    )
    duration: float = Field(
        ...,
        title="duration",
        description="Duration of flight edge",
        ge=0
    )
    max_crew: float = Field(
        ...,
        title="Max Crew",
        description="Crew capacity for flight",
        ge=0
    )
    max_cargo: float = Field(
        ...,
        title="Max Cargo",
        description="Cargo capacity for flight",
        ge=0
    )

