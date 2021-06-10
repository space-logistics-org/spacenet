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


class SurfaceEdge(Edge):
    distance = Column(Float)


class SpaceEdge(Edge):
    duration = Column(Float)


class FlightEdge(Edge):
    duration = Column(Float)
    max_crew = Column(Float)
    max_cargo = Column(Float)