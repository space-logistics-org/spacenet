"""
This module defines the database schema for elements and element subclasses.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from ..database import Base

from spacenet.schemas.element import ElementType

__all__ = [
    "ElementType",
    "Element",
    "ElementCarrier",
    "ResourceContainer",
    "PropulsiveVehicle",
    "SurfaceVehicle",
    "HumanAgent",
    "RoboticAgent",
]


class Element(Base):
    """
    A row representing a single element.
    """
    __tablename__ = "element"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    name = Column(String)
    description = Column(String)
    class_of_supply = Column(Integer)
    environment = Column(String)
    accommodation_mass = Column(Float)
    mass = Column(Float)
    volume = Column(Float)
    states = relationship("State", back_populates="element", passive_deletes=True)

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": ElementType.Element.value,
    }


class CargoCarrier(Element):
    """
    A row representing a cargo carrier.
    """

    __abstract__ = True

    @declared_attr
    def max_cargo_mass(cls):
        """
        :return: maximum cargo mass of the cargo carrier
        """
        return Element.__table__.c.get("max_cargo_mass", Column(Float))

    @declared_attr
    def max_cargo_volume(cls):
        """
        :return: maximum cargo volume of the cargo carrier
        """
        return Element.__table__.c.get("max_cargo_volume", Column(Float))


class ResourceContainer(CargoCarrier):
    """
    A row representing a resource container.
    """

    __mapper_args__ = {"polymorphic_identity": ElementType.ResourceContainer.value}


class ElementCarrier(CargoCarrier):
    """
    A row representing an element carrier.
    """
    cargo_environment = Column(String)

    __mapper_args__ = {"polymorphic_identity": ElementType.ElementCarrier.value}


class Agent(Element):
    """
    A row representing an agent.
    """
    __abstract__ = True

    @declared_attr
    def active_time_fraction(cls):
        """
        :return: fraction of time the agent can be working
        """
        return Element.__table__.c.get("active_time_fraction", Column(Float))


class HumanAgent(Agent):
    """
    A row representing a human agent, such as a crew member.
    """
    __mapper_args__ = {"polymorphic_identity": ElementType.HumanAgent.value}
    pass


class RoboticAgent(Agent):
    """
    A row representing a robotic agent.
    """
    __mapper_args__ = {"polymorphic_identity": ElementType.RoboticAgent.value}
    pass


class Vehicle(CargoCarrier):
    """
    A row representing a vehicle.
    """

    __abstract__ = True

    @declared_attr
    def max_crew(cls):
        """
        :return: maximum crew in vehicle
        """
        return Element.__table__.c.get("max_crew", Column(Integer))

    @declared_attr
    def max_fuel(cls):
        """
        :return: maximum fuel in the vehicle, in kg
        """
        return Element.__table__.c.get("max_fuel", Column(Float))


class PropulsiveVehicle(Vehicle):
    """
    A row representing a vehicle with its own propulsion.
    """
    isp = Column(Float)
    propellant_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": ElementType.PropulsiveVehicle.value}


class SurfaceVehicle(Vehicle):
    """
    A row representing a vehicle which moves on the surface.
    """
    max_speed = Column(Float)
    fuel_id = Column(Integer)

    __mapper_args__ = {"polymorphic_identity": ElementType.SurfaceVehicle.value}
