"""
This module defines the schemas for Read and Update variants of edges and the corresponding
subtypes.
"""

from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge
from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

__all__ = [
    "SurfaceEdge",
    "SurfaceEdgeRead",
    "SurfaceEdgeUpdate",
    "SpaceEdge",
    "SpaceEdgeRead",
    "SpaceEdgeUpdate",
    "FlightEdge",
    "FlightEdgeRead",
    "FlightEdgeUpdate",
]


class SurfaceEdgeRead(SurfaceEdge, ReadSchema):
    """
    Read variant of SurfaceEdge
    """
    pass


class SurfaceEdgeUpdate(SurfaceEdge, RequiresOnlyType):
    """
    Update variant of SurfaceEdge, requiring only a type field.
    """
    pass


class SpaceEdgeRead(SpaceEdge, ReadSchema):
    """
    Read variant of SpaceEdge
    """
    pass


class SpaceEdgeUpdate(SpaceEdge, RequiresOnlyType):
    """
    Update variant of SpaceEdge, requiring only a type field.
    """
    pass


class FlightEdgeRead(FlightEdge, ReadSchema):
    """
    Read variant of FlightEdge
    """
    pass


class FlightEdgeUpdate(FlightEdge, RequiresOnlyType):
    """
    Update variant of FlightEdge, requiring only a type field.
    """
    pass
