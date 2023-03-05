"""
Nodes define stable locations in the exploration network.
"""

from abc import ABC
from enum import Enum
from typing import Union

from pydantic import Field
from typing_extensions import Literal

from .body import Body
from .location import Location, LocationUUID


class NodeType(str, Enum):
    """
    An enumeration of node types.
    """

    SURFACE = "Surface Node"
    ORBITAL = "Orbital Node"
    LAGRANGE = "Lagrange Node"


class NodeUUID(LocationUUID):
    """
    Node referenced by unique identifier.
    """


class Node(Location, ABC):
    """
    Abstract base class for a node.
    """

    type: NodeType = Field(
        ...,
        title="Type",
        description="Node type",
    )
    body_1: Body = Field(
        Body.EARTH,
        title="Body 1",
        description="Primary planetary body",
    )


class SurfaceNode(Node):
    """
    Stable location on the surface of a planetary body.
    """

    type: Literal[NodeType.SURFACE] = Field(
        NodeType.SURFACE,
        title="Type",
        description="Node type",
    )
    latitude: float = Field(
        ...,
        title="Latitude",
        description="Latitude (decimal degrees, -90 to 90 inclusive)",
        ge=-90,
        le=90,
    )
    longitude: float = Field(
        ...,
        title="Longitude",
        description="Longitude (decimal degrees, -180 to 180 inclusive)",
        ge=-180,
        le=180,
    )


class OrbitalNode(Node):
    """
    Stable location orbiting a planetary body.
    """

    type: Literal[NodeType.ORBITAL] = Field(
        NodeType.ORBITAL,
        title="Type",
        description="Node type",
    )
    apoapsis: float = Field(
        ..., title="Apoapsis", description="Major orbit radius (m)", ge=0
    )
    periapsis: float = Field(
        ..., title="Periapsis", description="Minor orbit radius (m)", ge=0
    )
    inclination: float = Field(
        ...,
        title="Inclination",
        description="Orbit inclination (decimal degrees, 0 to 180 inclusive)",
        ge=0,
        le=180,
    )


class LagrangeNode(Node):
    """
    Stable location at a Lagrange point between two bodies.
    """

    type: Literal[NodeType.LAGRANGE] = Field(
        NodeType.LAGRANGE,
        title="Type",
        description="Node type",
    )
    body_2: Body = Field(
        ...,
        title="Body 2",
        description="Secondary Lagrange point body",
    )
    lp_number: int = Field(
        ..., title="LP Number", description="Lagrange point number (1 to 5)", ge=1, le=5
    )


AllNodes = Union[LagrangeNode, OrbitalNode, SurfaceNode]
