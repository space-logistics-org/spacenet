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
    cos = Column(Integer)
    units = Column(String)

    __mapper_args__ = {"polymorphic_identity": "resource"}


class DiscreteResource(Resource):
    @declared_attr
    def unit_mass(cls):
        return Resource.__table__.c.get("unit_mass", Column(Integer))

    @declared_attr
    def unit_volume(cls):
        return Resource.__table__.c.get("unit_volume", Column(Integer))

    __mapper_args__ = {"polymorphic_identity": ResourceType.discrete.value}


class ContinuousResource(Resource):
    @declared_attr
    def unit_mass(cls):
        return Resource.__table__.c.get("unit_mass", Column(Float))

    @declared_attr
    def unit_volume(cls):
        return Resource.__table__.c.get("unit_volume", Column(Float))

    __mapper_args__ = {"polymorphic_identity": ResourceType.continuous.value}
