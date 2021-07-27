from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field
from typing_extensions import Literal

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
]

from spacenet.schemas.types import SafeInt, SafeNonNegFloat, SafeNonNegInt
from .utilities import model_with_changed_field_types


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


REPLACED_EDGE_FIELDS = {"origin_id": UUID, "destination_id": UUID}


UUIDEdge = model_with_changed_field_types(
    "UUIDEdge", Edge, replaced_fields=REPLACED_EDGE_FIELDS,
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


UUIDSurfaceEdge = model_with_changed_field_types(
    "UUIDSurfaceEdge", SurfaceEdge, base=UUIDEdge, replaced_fields=REPLACED_EDGE_FIELDS
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


UUIDSpaceEdge = model_with_changed_field_types(
    "UUIDSpaceEdge", SpaceEdge, base=UUIDEdge, replaced_fields=REPLACED_EDGE_FIELDS
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


UUIDFlightEdge = model_with_changed_field_types(
    "UUIDFlightEdge", FlightEdge, base=UUIDEdge, replaced_fields=REPLACED_EDGE_FIELDS
)
