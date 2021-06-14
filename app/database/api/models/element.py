from sqlalchemy import Column, Integer, String, Float
from ..database import Base


class Element(Base):
    __tablename__ = "Elements"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    environment = Column(String)
    accommodation_mass = Column(Float)
    mass = Column(Float)
    volume = Column(Float)

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "element"}


class CargoCarrier(Element):

    __abstract__ = True

    max_cargo_mass = Column(Float)
    max_cargo_volume = Column(Float)


class ResourceContainer(CargoCarrier):

    __mapper_args__ = {"polymorphic_identity": "resource_container"}


class ElementCarrier(CargoCarrier):
    cargo_environment = Column(String)

    __mapper_args__ = {"polymorphic_identity": "element_carrier"}


class Agent(Element):
    __abstract__ = True

    active_time_fraction = Column(Float)


class HumanAgent(Agent):
    __mapper_args__ = {"polymorphic_identity": "human_agent"}
    pass


class RoboticAgent(Agent):
    __mapper_args__ = {"polymorphic_identity": "robotic_agent"}
    pass


class Vehicle(CargoCarrier):

    __abstract__ = True

    max_crew = Column(Integer)
    max_fuel = Column(Float)


class PropulsiveVehicle(Vehicle):
    isp = Column(Float)
    propellant_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": "propulsive_vehicle"}


class SurfaceVehicle(Vehicle):
    max_speed = Column(Float)
    fuel_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": "surface_vehicle"}
