from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class Edge(Base):
    __tablename__ = "Edges"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    origin_id = Column(Integer)
    destination_id = Column(Integer)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "edge"}


class SurfaceEdge(Edge):
    distance = Column(Float)

    __mapper_args__ = {"polymorphic_identity": "surface"}


class SpaceEdge(Edge):
    duration = Column(Float)

    __mapper_args__ = {"polymorphic_identity": "space"}


class FlightEdge(Edge):
    duration = Column(Float)
    max_crew = Column(Float)
    max_cargo = Column(Float)

    __mapper_args__ = {"polymorphic_identity": "flight"}