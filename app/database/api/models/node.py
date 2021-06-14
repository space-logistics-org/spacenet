from sqlalchemy import Column, Integer, String, Float
from ..database import Base

class Node(Base):

    __tablename__ = "Nodes"

    id = Column(Integer, primary_key = True, index = True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    body_1 = Column(String)

class SurfaceNode(Node):

    latitude = Column(Float)
    longitude = Column(Float)

class OrbitalNode(Node):

    apoapsis = Column(Float)
    periapsis = Column(Float)
    inclination = Column(Float)

class LagrangeNode(Node):

    body_2 = Column(String)
    lp_number = Column(Integer)
