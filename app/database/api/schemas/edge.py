from pydantic import Field
from spacenet.schemas import edge as schemas


class SurfaceEdgeCreate(schemas.SurfaceEdge):
    pass


class SurfaceEdge(schemas.SurfaceEdge):
    id: int = Field(
        ...,
        title="ID",
        description="Unique identifier"
    )

    class Config:
        orm_mode = True


class SpaceEdgeCreate(schemas.SpaceEdge):
    pass


class SpaceEdge(schemas.SpaceEdge):
    id: int = Field(
        ...,
        title="ID",
        description="Unique identifier"
    )

    class Config:
        orm_mode = True


class FlightEdgeCreate(schemas.FlightEdge):
    pass


class FlightEdge(schemas.FlightEdge):
    id: int = Field(
        ...,
        title="ID",
        description="Unique identifier"
    )

    class Config:
        orm_mode = True