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
    pass


class SurfaceEdgeUpdate(SurfaceEdge, RequiresOnlyType):
    pass


class SpaceEdgeRead(SpaceEdge, ReadSchema):
    pass


class SpaceEdgeUpdate(SpaceEdge, RequiresOnlyType):
    pass


class FlightEdgeRead(FlightEdge, ReadSchema):
    pass


class FlightEdgeUpdate(FlightEdge, RequiresOnlyType):
    pass
