from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode

from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType


class SurfaceNodeUpdate(SurfaceNode, RequiresOnlyType):
    pass


class SurfaceNodeRead(SurfaceNode, ReadSchema):
    pass


class OrbitalNodeUpdate(OrbitalNode, RequiresOnlyType):
    pass


class OrbitalNodeRead(OrbitalNode, ReadSchema):
    pass


class LagrangeNodeUpdate(LagrangeNode, RequiresOnlyType):
    pass


class LagrangeNodeRead(LagrangeNode, ReadSchema):
    pass
