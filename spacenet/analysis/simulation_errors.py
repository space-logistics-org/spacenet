from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SimError(BaseModel):
    timestamp: datetime
    description: str

    @staticmethod
    def does_not_exist(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(
            timestamp=timestamp, description=f"No entity with id {id_} in namespace"
        )

    @staticmethod
    def not_an_element(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(timestamp=timestamp, description=f"ID {id_} is not an element")

    @staticmethod
    def not_a_container(timestamp: datetime, id_: UUID) -> "SimError":
        return SimError(timestamp=timestamp, description=f"ID {id_} is not a container")

    @staticmethod
    def not_at_location(timestamp: datetime, id_: UUID, location: UUID) -> "SimError":
        return SimError(
            timestamp=timestamp, description=f"ID {id_} is not at location {location}"
        )
