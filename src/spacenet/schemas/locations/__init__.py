"""
Network components (nodes and edges) define stable locations in the static
exploration network at which elements can persist.
"""

from typing import Union

from .body import Body
from .burn import Burn
from .edges import AllEdges, EdgeType, EdgeUUID, FlightEdge, SpaceEdge, SurfaceEdge
from .location import Location, LocationUUID
from .network import Network
from .nodes import AllNodes, LagrangeNode, NodeType, NodeUUID, OrbitalNode, SurfaceNode

AllLocations = Union[AllEdges, AllNodes]
