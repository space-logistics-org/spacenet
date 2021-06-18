from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode

from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType


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
