from spacenet.schemas.resource import DiscreteResource, ContinuousResource
from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

__all__ = [
    "DiscreteResource",
    "ReadDiscrete",
    "UpdateDiscrete",
    "ContinuousResource",
    "ReadContinuous",
    "UpdateContinuous",
]


class ReadDiscrete(DiscreteResource, ReadSchema):
    pass


class UpdateDiscrete(DiscreteResource, RequiresOnlyType):
    pass


class ReadContinuous(ContinuousResource, ReadSchema):
    pass


class UpdateContinuous(ContinuousResource, RequiresOnlyType):
    pass
