from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class Element(Base):
    _tablename_ = "Elements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    environment = Column(String)
    accommodation_mass = Column(Float)
    mass = Column(Float)
    volume = Column(Float)


class CargoCarrier(Element):
    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)


class ResourceContainer(CargoCarrier):
    pass


class ElementCarrier(CargoCarrier):
    cargo_environment = Column(String)


class Agent(Element):
    active_time_fraction = Column(Float)


class HumanAgent(Agent):
    pass


class RoboticAgent(Agent):
    pass


class Vehicle(CargoCarrier):
    max_crew = Column(Integer)
    max_fuel = Column(Float)


class PropulsiveVehicle(Vehicle):
    isp = Column(Float)
    propellant_id = Column(Integer)


class SurfaceVehicle(Vehicle):
    max_speed = Column(Float)
    fuel_id = Column(Integer)
