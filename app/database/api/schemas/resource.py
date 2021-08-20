"""
This module defines the schemas for Read and Update variants of resources and the corresponding
subtypes. 

"""

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
    """
    Read variant of DiscreteResource schema
    """
    pass


class DiscreteUpdate(DiscreteResource, RequiresOnlyType):
    """
    Update variant of DiscreteResource schema
    """
    pass


class ContinuousRead(ContinuousResource, ReadSchema):
    """
    Read variant of ContinuousResource schema
    """
    pass


class ContinuousUpdate(ContinuousResource, RequiresOnlyType):
    """
    Update variant of ContinuousResource schema
    """
    pass
