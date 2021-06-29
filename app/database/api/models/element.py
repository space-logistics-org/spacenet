from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declared_attr, relationship
from ..database import Base

from spacenet.schemas.element import ElementKind

__all__ = [
    "ElementKind",
    "Element",
    "ElementCarrier",
    "ResourceContainer",
    "PropulsiveVehicle",
    "SurfaceVehicle",
    "HumanAgent",
    "RoboticAgent",
]


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
    associated_states = relationship(
        "State", back_populates="parent_element",
        cascade="all, delete",
        passive_deletes=True
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": ElementKind.Element.value,
    }


class CargoCarrier(Element):

    __abstract__ = True

    @declared_attr
    def max_cargo_mass(cls):
        return Element.__table__.c.get("max_cargo_mass", Column(Float))

    @declared_attr
    def max_cargo_volume(cls):
        return Element.__table__.c.get("max_cargo_volume", Column(Float))


class ResourceContainer(CargoCarrier):

    __mapper_args__ = {"polymorphic_identity": ElementKind.ResourceContainer.value}


class ElementCarrier(CargoCarrier):
    cargo_environment = Column(String)

    __mapper_args__ = {"polymorphic_identity": ElementKind.ElementCarrier.value}


class Agent(Element):
    __abstract__ = True

    @declared_attr
    def active_time_fraction(cls):
        return Element.__table__.c.get("active_time_fraction", Column(Float))


class HumanAgent(Agent):
    __mapper_args__ = {"polymorphic_identity": ElementKind.HumanAgent.value}
    pass


class RoboticAgent(Agent):
    __mapper_args__ = {"polymorphic_identity": ElementKind.RoboticAgent.value}
    pass


class Vehicle(CargoCarrier):

    __abstract__ = True

    @declared_attr
    def max_crew(cls):
        return Element.__table__.c.get("max_crew", Column(Integer))

    @declared_attr
    def max_fuel(cls):
        return Element.__table__.c.get("max_fuel", Column(Float))


class PropulsiveVehicle(Vehicle):
    isp = Column(Float)
    propellant_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": ElementKind.Propulsive.value}


class SurfaceVehicle(Vehicle):
    max_speed = Column(Float)
    fuel_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": ElementKind.Surface.value}
