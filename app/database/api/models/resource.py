from sqlalchemy import Column, Integer, String, Float
from ..database import Base


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
    unitmass = Column(Integer)
    unitvolume = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": "discrete"}


class ContinuousResource(Resource):
    unitmass = Column(Float)
    unitvolume = Column(Float)

    __mapper_args__ = {"polymorphic_identity": "continuous"}