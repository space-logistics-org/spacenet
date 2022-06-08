"""
This module defines errors which can be accumulated while running a simulation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


__all__ = [
    "SimError",
    "EntityNotAContainer",
    "EntityNotAnElement",
    "EntityDoesNotExist",
    "ElementNotAtLocation",
]

from ..schemas import PropulsiveBurn


class SimError(BaseModel):
    """
    The generic error type representing a recoverable error in simulation. Generally, these
    are recovered from by assuming the triggering event is successful. If that is not the case,
    the simulation may fail with an actual exception.
    """

    timestamp: Optional[datetime] = None
    description: str

    @staticmethod
    def does_not_exist(
        timestamp: datetime, id_: UUID, name: str
    ) -> "EntityDoesNotExist":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not existing
        """
        return EntityDoesNotExist.new(timestamp, id_, name)

    @staticmethod
    def not_an_element(
        timestamp: datetime, id_: UUID, name: str
    ) -> "EntityNotAnElement":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not being an element
        """
        return EntityNotAnElement.new(timestamp, id_, name)

    @staticmethod
    def not_a_container(
        timestamp: datetime, id_: UUID, name: str
    ) -> "EntityNotAContainer":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not being a container
        """
        return EntityNotAContainer.new(timestamp, id_, name)

    @staticmethod
    def not_at_location(
        timestamp: datetime, id_: UUID, location: UUID, name: str
    ) -> "ElementNotAtLocation":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param location: location of erring entity
        :param name: name of erring entity
        :return: an error representing an element not being at a location
        """
        return ElementNotAtLocation.new(timestamp, id_, location, name)

    @staticmethod
    def insufficient_fuel(
        event: PropulsiveBurn,
        timestamp: datetime
    ) -> "InsufficientFuelForBurn":
        """
        :param timestamp: error timestamp
        :param event: event which requires too much fuel to be satisfied
        :return: an error representing insufficient fuel to execute a PropulsiveBurn
        """
        return InsufficientFuelForBurn.new(event)


class EntityDoesNotExist(SimError):
    """
    An error representing that an entity does not exist.
    """

    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityDoesNotExist":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not existing
        """
        return EntityDoesNotExist(
            timestamp=timestamp,
            description=f"No entity ({name}) with id {id_} in namespace",
        )


class EntityNotAnElement(SimError):
    """
    An error representing that an entity is not an element.
    """

    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityNotAnElement":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not being an element
        """
        return EntityNotAnElement(
            timestamp=timestamp, description=f"{name} (ID={id_}) is not an element"
        )


class EntityNotAContainer(SimError):
    """
    An error representing that an entity is not a container.
    """

    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityNotAContainer":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param name: name of erring entity
        :return: an error representing an entity not being a container
        """
        return EntityNotAContainer(
            timestamp=timestamp, description=f"{name} (ID={id_}) is not a container"
        )


class ElementNotAtLocation(SimError):
    """
    An error representing that an entity is not present at a location it was expected to be at.
    """

    @staticmethod
    def new(
        timestamp: datetime, id_: UUID, location: UUID, name: str
    ) -> "ElementNotAtLocation":
        """
        :param timestamp: error timestamp
        :param id_: id of erring entity
        :param location: location of erring entity
        :param name: name of erring entity
        :return: an error representing an element not being at a location
        """
        return ElementNotAtLocation(
            timestamp=timestamp,
            description=f"{name} (ID={id_}) is not at location {location}",
        )


class InsufficientFuelForBurn(SimError):
    """
    An error representing insufficient fuel to execute a PropulsiveBurn.
    """

    @staticmethod
    def new(
            timestamp: datetime, event: PropulsiveBurn
    ) -> "InsufficientFuelForBurn":
        """
        :param timestamp: error timestamp
        :param event: event which requires too much fuel to be satisfied
        :return: an error representing insufficient fuel to execute a PropulsiveBurn
        """
        return InsufficientFuelForBurn(
            timestamp=timestamp,
            description=f"The propulsive burn {event.name} at time {timestamp} does not have "
                        f"sufficient fuel for the specified velocity change"
        )
