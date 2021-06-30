from math import inf

from pydantic import BaseModel, Field, confloat, conint

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

    time: confloat(gt=0, lt=inf) = Field(
        ...,
        title="Time",
        description="The execution time, relative to the start of the mission. "
    )

    priority: conint(ge=1, le=5) = Field(
        ...,
        title="Priority",
        description="Importance of mission event",
        ge=1,
        le=5
    )

    eva_duration: confloat(gt=0, lt=inf) = Field(
        ...,
        title="EVA Duration",
        description="The duration of the EVA"
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
    duration: confloat(gt=0, lt=inf) = Field(
        ...,
        title="Exploration Duration",
        description="The duration of the exploration"
    )
    eva_per_week: conint(gt=0, le=SQLITE_MAX_INT) = Field(
        ...,
        title="EVAs per week",
        description="Number of EVAs to be performed a week"
    )
