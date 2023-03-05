"""
This module defines the schemas for Read and Update variants of nodes and the corresponding
subtypes. 
"""

from spacenet.schemas.mixins import ReadSchema, RequiresOnlyType
from spacenet.schemas.node import LagrangeNode, OrbitalNode, SurfaceNode

__all__ = [
    "LagrangeNode",
    "LagrangeNodeRead",
    "LagrangeNodeUpdate",
    "OrbitalNode",
    "OrbitalNodeRead",
    "OrbitalNodeUpdate",
    "SurfaceNode",
    "SurfaceNodeRead",
    "SurfaceNodeUpdate",
]


class SurfaceNodeUpdate(SurfaceNode, RequiresOnlyType):
    """
    Update schema variant for surface node.
    """
    pass


class SurfaceNodeRead(SurfaceNode, ReadSchema):
    """
    Read schema variant for surface node.
    """
    pass


class OrbitalNodeUpdate(OrbitalNode, RequiresOnlyType):
    """
    Update schema variant for orbital node.
    """
    pass


class OrbitalNodeRead(OrbitalNode, ReadSchema):
    """
    Read schema variant for orbital node.
    """
    pass


class LagrangeNodeUpdate(LagrangeNode, RequiresOnlyType):
    """
    Update schema variant for lagrange node.
    """
    pass


class LagrangeNodeRead(LagrangeNode, ReadSchema):
    """
    Read schema variant for lagrange node.
    """
    pass
