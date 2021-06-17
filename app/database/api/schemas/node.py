from spacenet.schemas import node as schemas
from pydantic import Field

from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

class SurfaceNodeCreate(schemas.SurfaceNode):
    pass


class SurfaceNode(schemas.SurfaceNode):
    id: int = Field(
        ...,
        title="ID",
        description="Unique Identifier"
    )

    class Config:
        orm_mode = True


class OrbitalNodeCreate(schemas.OrbitalNode):
    pass


class OrbitalNode(schemas.OrbitalNode):
    id: int = Field(
        ...,
        title="ID",
        description="Unique identifier"
    )

    class Config:
        orm_mode = True


class LagrangeNodeCreate(schemas.LagrangeNode):
    pass


class LagrangeNode(schemas.LagrangeNode):
    id: int = Field(
        ...,
        title="ID",
        description="Unique identifier"
    )

    class Config:
        orm_mode = True

class UpdateSurfaceNode(SurfaceNode, RequiresOnlyType):
    pass


class ReadSurfaceNode(SurfaceNode, ReadSchema):
    pass


class UpdateOrbitalNode(OrbitalNode, RequiresOnlyType):
    pass


class ReadOrbitalNode(OrbitalNode, ReadSchema):
    pass


class UpdateLagrangeNode(LagrangeNode, RequiresOnlyType):
    pass


class ReadLagrangeNode(LagrangeNode, ReadSchema):
    pass
