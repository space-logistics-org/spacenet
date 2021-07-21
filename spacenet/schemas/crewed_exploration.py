from datetime import timedelta
from math import inf
from uuid import UUID

from pydantic import Field

from spacenet.constants import SQLITE_MAX_INT
from spacenet.schemas import Event


class CrewedExploration(Event):
    """
    Crewed Exploration Event schema
    """

    name: str = Field(..., title="Name", description="Crewed EVA name")

    node: UUID = Field(..., title="Node", description="The location of the Crewed EVA")

    time: timedelta = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. ",
        gt=0,
        lt=inf,
    )

    eva_duration: timedelta = Field(
        ..., title="EVA Duration", description="The duration of the EVA", gt=0, lt=inf
    )

    crew_location: UUID = Field(
        ...,
        title="Crew Location",
        description="The location of the crew that will be used for the EVA",
    )

    crew: list = Field(  # TODO: parametrize this
        ..., title="Crew", description="List of the crew selected for the EVA"
    )
    duration: timedelta = Field(
        ...,
        title="Exploration Duration",
        description="The duration of the exploration",
        gt=0,
        lt=inf,
    )
    eva_per_week: int = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week",
        gt=0,
        le=SQLITE_MAX_INT,
    )
