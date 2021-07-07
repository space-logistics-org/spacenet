from math import inf

from pydantic import BaseModel, Field

from spacenet.constants import SQLITE_MAX_INT


class CrewedExploration(BaseModel):
    """
    Crewed Exploration Event schema
    """
    name: str = Field(
        ...,
        title="Name",
        description="Crewed EVA name"
    )

    node: str = Field(
        ...,
        title="Node",
        description="The location of the Crewed EVA"
    )

    time: float = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. ",
        gt=0,
        lt=inf,
    )

    priority: int = Field(
        ...,
        title="Priority",
        description="Importance of mission event",
        ge=1,
        le=5
    )

    eva_duration: float = Field(
        ...,
        title="EVA Duration",
        description="The duration of the EVA",
        gt=0,
        lt=inf
    )

    crew_location: str = Field(
        ...,
        title="Crew Location",
        description="The location of the crew that will be used for the EVA"
    )

    crew: list = Field(
        ...,
        title="Crew",
        description="List of the crew selected for the EVA"
    )
    duration: float = Field(
        ...,
        title="Exploration Duration",
        description="The duration of the exploration",
        gt=0,
        lt=inf
    )
    eva_per_week: int = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week",
        gt=0,
        le=SQLITE_MAX_INT
    )
