from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declared_attr

from ..database import Base
from spacenet.schemas.resource import ResourceType


class Resource(Base):
    __tablename__ = "Resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    units = Column(String)

    __mapper_args__ = {"polymorphic_identity": "resource", "polymorphic_on": type}


class DiscreteResource(Resource):
    unit_mass_i = Column(Integer)
    unit_volume_i = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": ResourceType.discrete.value}


class ContinuousResource(Resource):
    unit_mass_f = Column(Float)
    unit_volume_f = Column(Float)

    __mapper_args__ = {"polymorphic_identity": ResourceType.continuous.value}
