from spacenet.schemas.edge import SurfaceEdge, SpaceEdge, FlightEdge
from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

__all__ = ["SurfaceEdge", "ReadSurfaceEdge", "UpdateSurfaceEdge",
           "SpaceEdge", "ReadSpaceEdge", "UpdateSpaceEdge",
           "FlightEdge", "ReadFlightEdge", "UpdateFlightEdge"]

class ReadSurfaceEdge(SurfaceEdge, ReadSchema):
    pass

class UpdateSurfaceEdge(SurfaceEdge, RequiresOnlyType):
    pass

class ReadSpaceEdge(SpaceEdge, ReadSchema):
    pass

class UpdateSpaceEdge(SpaceEdge, RequiresOnlyType):
    pass

class ReadFlightEdge(FlightEdge, ReadSchema):
    pass

class UpdateFLightEdge(FlightEdge, RequiresOnlyType):
    pass
