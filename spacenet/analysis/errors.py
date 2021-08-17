"""
This module defines errors which can be accumulated while running a simulation.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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
        return EntityDoesNotExist.new(timestamp, id_, name)

    @staticmethod
    def not_an_element(
        timestamp: datetime, id_: UUID, name: str
    ) -> "EntityNotAnElement":
        return EntityNotAnElement.new(timestamp, id_, name)

    @staticmethod
    def not_a_container(
        timestamp: datetime, id_: UUID, name: str
    ) -> "EntityNotAContainer":
        return EntityNotAContainer.new(timestamp, id_, name)

    @staticmethod
    def not_at_location(
        timestamp: datetime, id_: UUID, location: UUID, name: str
    ) -> "ElementNotAtLocation":
        return ElementNotAtLocation.new(timestamp, id_, location, name)


class EntityDoesNotExist(SimError):
    """
    An error representing that an entity does not exist.
    """

    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityDoesNotExist":
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
        return EntityNotAnElement(
            timestamp=timestamp, description=f"{name} (ID={id_}) is not an element"
        )


class EntityNotAContainer(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityNotAContainer":
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
        return ElementNotAtLocation(
            timestamp=timestamp,
            description=f"{name} (ID={id_}) is not at location {location}",
        )
