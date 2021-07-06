from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType
from spacenet.schemas.resource import ContinuousResource, DiscreteResource

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
