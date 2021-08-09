from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SimError(BaseModel):
    timestamp: Optional[datetime] = None
    description: str

    @staticmethod
    def does_not_exist(timestamp: datetime, id_: UUID, name: str) -> "EntityDoesNotExist":
        return EntityDoesNotExist.new(timestamp, id_, name)

    @staticmethod
    def not_an_element(timestamp: datetime, id_: UUID, name: str) -> "EntityNotAnElement":
        return EntityNotAnElement.new(timestamp, id_, name)

    @staticmethod
    def not_a_container(timestamp: datetime, id_: UUID, name: str) -> "EntityNotAContainer":
        return EntityNotAContainer.new(timestamp, id_, name)

    @staticmethod
    def not_at_location(
        timestamp: datetime, id_: UUID, location: UUID, name: str
    ) -> "EntityNotAtLocation":
        return EntityNotAtLocation.new(timestamp, id_, location, name)


class EntityDoesNotExist(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID, name: str) -> "EntityDoesNotExist":
        return EntityDoesNotExist(
            timestamp=timestamp, description=f"No entity ({name}) with id {id_} in namespace"
        )


class EntityNotAnElement(SimError):
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


class EntityNotAtLocation(SimError):
    @staticmethod
    def new(timestamp: datetime, id_: UUID, location: UUID, name: str) -> "EntityNotAtLocation":
        return EntityNotAtLocation(
            timestamp=timestamp, description=f"{name} (ID={id_}) is not at location {location}"
        )
