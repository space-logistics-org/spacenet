"""Defines object schemas for locations."""

from .node import (
    Body,
    NodeType,
    NodeUUID,
    LagrangeNode,
    OrbitalNode,
    SurfaceNode,
    AllNodes,
)
from .edge import Burn, EdgeType, EdgeUUID, FlightEdge, SpaceEdge, SurfaceEdge, AllEdges
