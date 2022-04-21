"""
This module defines schemas for network nodes.
"""
from enum import Enum
from typing import List, Optional, Union
from uuid import uuid4, UUID

from pydantic import Field, confloat, conint
from typing_extensions import Literal

from .types import SafeNonNegFloat
from .mixins import ImmutableBaseModel
from .inst_element import InstElementUUID
from .resource import ResourceUUID

__all__ = ["NodeUUID", "Body", "NodeType", "LagrangeNode", "OrbitalNode", "SurfaceNode", "AllNodes"]


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

class NodeUUID(ImmutableBaseModel):
    """
    A base class which defines a node by its UUID only.

    :param UUID id: unique identifier for node
    """
    id: UUID = Field(default_factory=uuid4, description="unique identifier for node")


class Node(NodeUUID):
    """
    Base class for all nodes.


    :param str name: name of node
    :param str description: short description of the node
    :param Body body_1: Body of surface location, body of orbit, or body of major Lagrange point
    :param [InstElementUUID] contents: UUIDs of elements stored at this node during the spatial simulation
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
    contents: List[InstElementUUID] = Field([], title="Contents", description="elements stored at this node during the spatial simulation")


class SurfaceNode(Node):
    """
    A node on the surface of a body.

    :param SurfaceNode type: Type of node (surface, orbital, or lagrange)
    :param latitude: Latitude (decimal degrees)
    :type latitude: float from -90 to 90
    :param longitude: Longitude (decimal degrees)
    :type longitude: float from -90 to 90
    """

    type: Literal[NodeType.Surface] = Field(
        NodeType.Surface, title="Type", description="Type of node (surface, orbital, or lagrange)",
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

    :param OrbitalNode type: Type of node (surface, orbital, or lagrange)
    :param NonNegFloat apoapsis: Major radius of orbit
    :param NonNegFloat periapsis: Minor radius of orbit
    :param inclination: Inclination of orbit
    :type inclination: float from -90 to 90
    """

    type: Literal[NodeType.Orbital] = Field(
        NodeType.Orbital, title="Type", description="Type of node (surface, orbital, or lagrange)",
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

    :param LagrangeNode type: Type of node (surface, orbital, or lagrange)
    :param Body body_2: Minor body of Lagrange node
    :param lp_number: Number of Lagrange point
    :type lp_number: int from 1 to 5
    """

    type: Literal[NodeType.Lagrange] = Field(
        NodeType.Lagrange, title="Type", description="Type of node (surface, orbital, or lagrange)",
    )
    body_2: Body = Field(
        ..., title="Body 2", description="Minor body of Lagrange node",
    )
    lp_number: conint(ge=1, le=5, strict=True) = Field(
        ..., title="LP Number", description="Number of Lagrange point"
    )


AllNodes = Union[LagrangeNode, OrbitalNode, SurfaceNode]
