from enum import Enum
from typing import Union

from pydantic import Field, confloat, conint
from typing_extensions import Literal

from .types import SafeNonNegFloat
from .mixins import ImmutableBaseModel

__all__ = ["Body", "NodeType", "LagrangeNode", "OrbitalNode", "SurfaceNode", "AllNodes"]


AllNodes = Union["LagrangeNode", "OrbitalNode", "SurfaceNode"]


class Body(str, Enum):
    """
    An enumeration of the possible bodies for a node.
    """

    Sun = "Sun"
    Earth = "Earth"
    Moon = "Moon"
    Mars = "Mars"


class NodeType(str, Enum):
    """
    An enumeration of the three types of nodes.
    """

    Surface = "SurfaceNode"
    Orbital = "OrbitalNode"
    Lagrange = "LagrangeNode"


class Node(ImmutableBaseModel):
    """
    Base class for all nodes.
    """

    name: str = Field(..., title="Name", description="name of the node")
    description: str = Field(
        ..., title="Description", description="short description of the node"
    )
    body_1: Body = Field(
        ...,
        title="Body 1",
        description="Body of surface location, body of orbit, or body of major Lagrange point",
    )


class SurfaceNode(Node):
    """
    A node on the surface of a body.
    """

    type: Literal[NodeType.Surface] = Field(
        ..., title="Type", description="Type of node (surface, orbital, or lagrange)",
    )
    latitude: confloat(ge=-90, le=90) = Field(
        ..., title="Latitude", description="Latitude (decimal degrees)"
    )
    longitude: confloat(ge=-180, le=180) = Field(
        ..., title="Longitude", description="Longitude (decimal degrees)",
    )


class OrbitalNode(Node):
    """
    A node orbiting a body.
    """

    type: Literal[NodeType.Orbital] = Field(
        ..., title="Type", description="Type of node (surface, orbital, or lagrange)",
    )
    apoapsis: SafeNonNegFloat = Field(
        ..., title="Apoapsis", description="Major radius of orbit"
    )
    periapsis: SafeNonNegFloat = Field(
        ..., title="Periapsis", description="Minor radius of orbit"
    )
    inclination: confloat(ge=0, le=90) = Field(
        ..., title="Inclination", description="Inclination of orbit"
    )


class LagrangeNode(Node):
    """
    A node at a Lagrange point of two bodies.
    """

    type: Literal[NodeType.Lagrange] = Field(
        ..., title="Type", description="Type of node (surface, orbital, or lagrange)",
    )
    body_2: Body = Field(
        ..., title="Body 2", description="Minor body of Lagrange node",
    )
    lp_number: conint(ge=1, le=5, strict=True) = Field(
        ..., title="LP Number", description="Number of Lagrange point"
    )
