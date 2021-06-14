from sqlalchemy import Column, Integer, String, Float
from ..database import Base

class Element(Base):
    
    _tablename_ = "Elements"

    id = Column(Integer, primary_key = True, index = True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    environment = Column(String)
    accommodation_mass = Column(Float)
    mass = Column(Float)
    volume = Column(Float)

class ResourceContainer(Element):

    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)

class ElementCarrier(Element):

    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)
    cargo_environment = Column(String)

class HumanAgent(Element):

    active_time_fraction = Column(Float)

class RoboticAgent(Element):

    active_time_fraction = Column(Float)

class PropulsiveVehicle(Element):

    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)
    max_crew = Column(Integer)
    isp = Column(Float)
    max_fuel = Column(Float)
    propellant_id = Column(Integer)

class SurfaceVehicle(Element):

    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)
    max_crew = Column(Integer)
    max_speed = Column(Float)
    max_fuel = Column(Float)
    fuel_id = Column(Integer)
