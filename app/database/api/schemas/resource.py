from spacenet.schemas.resource import DiscreteResource, ContinuousResource
from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType

__all__ = [
    "DiscreteResource",
    "DiscreteRead",
    "DiscreteUpdate",
    "ContinuousResource",
    "ContinuousRead",
    "ContinuousUpdate",
]


class DiscreteRead(DiscreteResource, ReadSchema):
    pass


class DiscreteUpdate(DiscreteResource, RequiresOnlyType):
    pass


class ContinuousRead(ContinuousResource, ReadSchema):
    pass


class ContinuousUpdate(ContinuousResource, RequiresOnlyType):
    pass
