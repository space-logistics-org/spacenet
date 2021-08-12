from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declared_attr

from ..database import Base
from spacenet.schemas.edge import EdgeType

__all__ = ["EdgeType", "Edge", "FlightEdge", "SpaceEdge", "SurfaceEdge"]


class Edge(Base):
    __tablename__ = "edge"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    origin_id = Column(Integer)
    destination_id = Column(Integer)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "edge"}


class SurfaceEdge(Edge):
    distance = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Surface.value}


class EdgeWithDuration(Edge):
    __abstract__ = True

    @declared_attr
    def duration(cls):
        return Edge.__table__.c.get("duration", Column(Float))


class SpaceEdge(EdgeWithDuration):

    delta_v = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Space.value}


class FlightEdge(EdgeWithDuration):
    max_crew = Column(Integer)
    max_cargo = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Flight.value}
