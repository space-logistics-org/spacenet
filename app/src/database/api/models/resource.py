"""
This module defines the database schema for resources and resource subclasses.
"""

from sqlalchemy import Column, Integer, String, Float

from ..database import Base
from spacenet.src.schemas.resource import ResourceType


__all__ = ["Resource", "ResourceType", "ContinuousResource", "DiscreteResource"]


class Resource(Base):
    """
    A row representing a single resource, can be continuous or discrete.
    """
    __tablename__ = "resource"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    units = Column(String)
    unit_mass = Column(Float)
    unit_volume = Column(Float)

    __mapper_args__ = {"polymorphic_identity": "resource", "polymorphic_on": type}


class DiscreteResource(Resource):
    """
    A row representing a single discrete resource.
    """

    __mapper_args__ = {"polymorphic_identity": ResourceType.Discrete.value}


class ContinuousResource(Resource):
    """
    A row representing a single continuous resource.
    """

    __mapper_args__ = {"polymorphic_identity": ResourceType.Continuous.value}
