"""Defines object schemas for nodes."""

from abc import ABC
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID
from datetime import timedelta

from pydantic import Field
from typing_extensions import Literal

from ..utils import ImmutableBaseModel, SafeNonNegFloat, SafeNonNegInt
from ..elements import InstElementUUID


class EdgeType(str, Enum):
    """
    An enumeration of edge types.
    """

    SURFACE = "Surface Edge"
    SPACE = "Space Edge"
    FLIGHT = "Flight Edge"


class EdgeUUID(ImmutableBaseModel):
    """
    Edge referenced by unique identifer.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Edge(EdgeUUID, ABC):
    """
    Abstract base class for a valid trajectory between two nodes.

    :param str name: edge name
    :param SurfaceEdge type: edge type
    :param str description: short description (optional)
    :param UUID origin: origin node unique identifier
    :param UUID destination: destination node unique identifier
    :param [UUID] contents: list of elements (by unique identifier) located at this edge

    """

    name: str = Field(
        ..., title="Name", description="Edge name",
    )
    type: EdgeType = Field(
        ..., title="Type", description="Edge type",
    )
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description",
    )
    origin: UUID = Field(
        ..., title="Origin Node", description="Origin node unique identifier"
    )
    destination: UUID = Field(
        ..., title="Destination Node", description="Destination node unique identifier",
    )
    contents: List[InstElementUUID] = Field(
        [],
        title="Contents",
        description="List of elements (by unique identifier) located at this edge",
    )


class SurfaceEdge(Edge):
    """
    Surface trajectory between two surface nodes.

    :param NonNegFloat distance: distance (m) of surface trajectory
    """

    type: Literal[EdgeType.SURFACE] = Field(
        EdgeType.SURFACE, title="Type", description="Edge type",
    )
    distance: SafeNonNegFloat = Field(
        ..., title="Distance", description="Distance (m) of surface trajectory"
    )


class BurnUUID(ImmutableBaseModel):
    """
    Propulsive burn referenced by unique identifier.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Burn(BurnUUID):
    """
    Impulsive propulsive burn triggered at a designated time during a space
    transport to generate a target change in velocity (delta-V).

    :param timedelta time: time relative to the start of the space transport
    :param SafeNonNegFloat delta_v: change in velocity (m/s) to be achieved
    """

    time: timedelta = Field(
        ..., description="Time relative to the start of the space transport"
    )
    delta_v: SafeNonNegFloat = Field(
        ..., description="Change in velocity (m/s) to be achieved"
    )


class SpaceEdge(Edge):
    """
    An in-space trajectory between two nodes using a propulsive burn sequence.

    :param timedelta duration: duration of the in-space trajectory
    :param [Burn] burns: list of propulsive burns required to traverse the edge
    """

    type: Literal[EdgeType.SPACE] = Field(
        EdgeType.SPACE, title="Type", description="Edge type",
    )
    duration: timedelta = Field(
        ..., title="Duration", description="Duration of space edge"
    )
    burns: List[Burn] = Field(
        ...,
        title="Burns",
        description="List of propulsive burns required to traverse the edge",
    )


class FlightEdge(Edge):
    """
    A trajectory between two nodes that is known to be feasible for a given
    cargo (mass) and crew capacity under a specified flight architecture.

    :param timedelta duration: duration of traversal between nodes
    :param SafeNonNegInt max_crew: maximum number of crew to be transported
    :param SafeNonNegFloat max_cargo: maximum cargo (kg) to be transported
    """

    type: Literal[EdgeType.FLIGHT] = Field(
        EdgeType.FLIGHT, title="Type", description="Edge type",
    )
    duration: timedelta = Field(
        ..., title="duration", description="Duration of traversal between nodes"
    )
    max_crew: SafeNonNegInt = Field(
        ..., title="Max Crew", description="Maximum number of crew to be transported",
    )
    max_cargo: SafeNonNegFloat = Field(
        ..., title="Max Cargo", description="Maximum cargo (kg) to be transported"
    )


AllEdges = Union[FlightEdge, SpaceEdge, SurfaceEdge]
