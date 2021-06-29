from sqlalchemy import Column, Integer, String, Float

from ..database import Base
from spacenet.schemas.resource import ResourceType


__all__ = ["Resource", "ResourceType", "ContinuousResource", "DiscreteResource"]


class Resource(Base):
    __tablename__ = "Resources"

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

    __mapper_args__ = {"polymorphic_identity": ResourceType.discrete.value}


class ContinuousResource(Resource):

    __mapper_args__ = {"polymorphic_identity": ResourceType.continuous.value}
