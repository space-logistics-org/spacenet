from pydantic import BaseModel, Field
from enum import Enum


class Body(str, Enum):
    """
    An ennumeration of the possible bodies for a node.
    """

    Sun = "Sun"
    Earth = "Earth"
    Moon = "Moon"
    Mars = "Mars"


class NodeType(str, Enum):
    """
    An ennumeration of the three types of nodes.
    """

    Surface = "Surface"
    Orbital = "Orbital"
    Lagrange = "Lagrange"



class Node(BaseModel):
    """
    Base class for all nodes.
    """
    name: str = Field(
        ...,
        title="Name",
        description="name of the node"
    )
    description: str = Field(
        ...,
        title="Description",
        description="short description of the node"
    )
    body_1: Body = Field(
        ...,
        title="Body 1",
        description="Body of surface location, body of orbit, or body of major Lagrange point"
    )


class SurfaceNode(Node):
    """
    A node on the surface of a body.
    """
    type: NodeType = Field(
        default=NodeType.Surface,
        title="Type",
        description="Type of node (surface, orbital, or lagrange)",
        const=True
    )
    latitude: float = Field(
        ...,
        title="Latitude",
        description="Latitude (decimal degrees)",
        ge=-90,
        le=90
    )
    longitude: float = Field(
        ...,
        title="Longitude",
        description="Longitude (decimal degrees)",
        ge=-180,
        le=180
    )


class OrbitalNode(Node):
    """
    A node orbiting a body.
    """
    type: NodeType = Field(
        default=NodeType.Orbital,
        title="Type",
        description="Type of node (surface, orbital, or lagrange)",
        const=True
    )
    apoapsis: float = Field(
        ...,
        title="Apoapsis",
        description="Major radius of orbit",
        ge=0
    )
    periapsis: float = Field(
        ...,
        title="Periapsis",
        description="Minor radius of orbit",
        ge=0
    )
    inclination: float = Field(
        ...,
        title="Inclination",
        description="Inclination of orbit",
        ge=0
    )


class LagrangeNode(Node):
    """
    A node at a Lagrange point of two bodies.
    """
    type: NodeType = Field(
        default=NodeType.Lagrange,
        title="Type",
        description="Type of node (surface, orbital, or lagrange)",
        const=True
    )
    body_2: Body = Field(
        ...,
        title="Body 2",
        description="Minor body of Lagrange node",
    )
    lp_number: int = Field(
        ...,
        title="LP Number",
        description="Number of Lagrange point",
        ge=1,
        le=5
    )