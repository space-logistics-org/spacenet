from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SimError(BaseModel):
    timestamp: Optional[datetime] = None
    description: str

    @staticmethod
    def does_not_exist(timestamp: datetime, id_: UUID) -> "EntityDoesNotExist":
        return EntityDoesNotExist.new(timestamp, id_)

    @staticmethod
    def not_an_element(timestamp: datetime, id_: UUID) -> "EntityNotAnElement":
        return EntityNotAnElement.new(timestamp, id_)

    @staticmethod
    def not_a_container(timestamp: datetime, id_: UUID) -> "EntityNotAContainer":
        return EntityNotAContainer.new(timestamp, id_)

    @staticmethod
    def not_at_location(
        timestamp: datetime, id_: UUID, location: UUID
    ) -> "EntityNotAtLocation":
        return EntityNotAtLocation.new(timestamp, id_, location)


class EntityDoesNotExist(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID) -> "EntityDoesNotExist":
        return EntityDoesNotExist(
            timestamp=timestamp, description=f"No entity with id {id_} in namespace"
        )


class EntityNotAnElement(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID) -> "EntityNotAnElement":
        return EntityNotAnElement(
            timestamp=timestamp, description=f"ID {id_} is not an element"
        )


class EntityNotAContainer(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID) -> "EntityNotAContainer":
        return EntityNotAContainer(
            timestamp=timestamp, description=f"ID {id_} is not a container"
        )


class EntityNotAtLocation(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID, location: UUID) -> "EntityNotAtLocation":
        return EntityNotAtLocation(
            timestamp=timestamp, description=f"ID {id_} is not at location {location}"
        )
