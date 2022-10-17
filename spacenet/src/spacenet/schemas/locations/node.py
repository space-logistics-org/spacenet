"""Defines object schemas for edges."""

from abc import ABC
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import Field, confloat, conint
from typing_extensions import Literal

from ..utils import SafeNonNegFloat, ImmutableBaseModel
from ..elements import InstElementUUID


class Body(str, Enum):
    """
    An enumeration of planetary bodies.
    """

    SUN = "Sun"
    EARTH = "Earth"
    MOON = "Moon"
    MARS = "Mars"


class NodeType(str, Enum):
    """
    An enumeration of node types.
    """

    SURFACE = "Surface Node"
    ORBITAL = "Orbital Node"
    LAGRANGE = "Lagrange Node"


class NodeUUID(ImmutableBaseModel):
    """
    Node referenced by unique identifier.

    :param UUID id: unique identifier
    """

    id: UUID = Field(default_factory=uuid4, description="Unique identifier")


class Node(NodeUUID, ABC):
    """
    Abstract base class for a stable location.

    :param str name: node name
    :param NodeType type: node type
    :param str description: short description (optional)
    :param Body body_1: primary planetary body
    :param [UUID] contents: list of elements (by unique identifier) located at this node
    """

    name: str = Field(..., title="Name", description="Node name")
    type: NodeType = Field(
        ..., title="Type", description="Node type",
    )
    description: Optional[str] = Field(
        default=None, title="Description", description="Short description",
    )
    body_1: Body = Field(
        ..., title="Body 1", description="Primary planetary body",
    )
    contents: List[InstElementUUID] = Field(
        [],
        title="Contents",
        description="List of elements (by unique identifier) located at this node",
    )


class SurfaceNode(Node):
    """
    Stable location on the surface of a planetary body.

    :param float latitude: Latitude (decimal degrees, -90 to 90 inclusive)
    :param float longitude: Longitude (decimal degrees, -180 to 180 inclusive)
    """

    type: Literal[NodeType.SURFACE] = Field(
        NodeType.SURFACE, title="Type", description="Node type",
    )
    latitude: confloat(ge=-90, le=90) = Field(
        ...,
        title="Latitude",
        description="Latitude (decimal degrees, -90 to 90 inclusive)",
    )
    longitude: confloat(ge=-180, le=180) = Field(
        ...,
        title="Longitude",
        description="Longitude (decimal degrees, -180 to 180 inclusive)",
    )


class OrbitalNode(Node):
    """
    Stable location orbiting a planetary body.

    :param NonNegFloat apoapsis: major orbit radius (m)
    :param NonNegFloat periapsis: minor orbit radius (m)
    :param float inclination: orbit inclination (decimal degrees, 0 to 180 inclusive)
    """

    type: Literal[NodeType.ORBITAL] = Field(
        NodeType.ORBITAL, title="Type", description="Node type",
    )
    apoapsis: SafeNonNegFloat = Field(
        ..., title="Apoapsis", description="Major orbit radius (m)"
    )
    periapsis: SafeNonNegFloat = Field(
        ..., title="Periapsis", description="Minor orbit radius (m)"
    )
    inclination: confloat(ge=0, le=180) = Field(
        ...,
        title="Inclination",
        description="Orbit inclination (decimal degrees, 0 to 180 inclusive)",
    )


class LagrangeNode(Node):
    """
    Stable location at a Lagrange point between two bodies.

    :param Body body_2: secondary Lagrange point body
    :param int lp_number: Lagrange point number (1 to 5)
    """

    type: Literal[NodeType.LAGRANGE] = Field(
        NodeType.LAGRANGE, title="Type", description="Node type",
    )
    body_2: Body = Field(
        ..., title="Body 2", description="Secondary Lagrange point body",
    )
    lp_number: conint(ge=1, le=5, strict=True) = Field(
        ..., title="LP Number", description="Lagrange point number (1 to 5)"
    )


AllNodes = Union[LagrangeNode, OrbitalNode, SurfaceNode]
