"""
This module defines the database schema for edges and edge subclasses.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declared_attr

from ..database import Base
from spacenet.schemas.edge import EdgeType

__all__ = ["EdgeType", "Edge", "FlightEdge", "SpaceEdge", "SurfaceEdge"]


class Edge(Base):
    """
    A row representing a single edge.
    """
    __tablename__ = "edge"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    origin_id = Column(Integer)
    destination_id = Column(Integer)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "edge"}


class SurfaceEdge(Edge):
    """
    A row representing a single surface edge.
    """
    distance = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Surface.value}


class HasDuration(Base):
    """
    A row representing an edge with an attribute Duration.
    """
    __abstract__ = True

    @declared_attr
    def duration(cls):
        return Edge.__table__.c.get("duration", Column(Float))


class SpaceEdge(Edge, HasDuration):
    """
    A row representing an edge between two nodes traversed via propulsive burns.
    """

    delta_v = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Space.value}


class FlightEdge(Edge, HasDuration):
    """
    A row representing an edge which the vehicle is known to be able to traverse with
    sufficient fuel.
    """
    max_crew = Column(Integer)
    max_cargo = Column(Float)

    __mapper_args__ = {"polymorphic_identity": EdgeType.Flight.value}
