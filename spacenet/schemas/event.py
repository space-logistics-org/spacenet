from datetime import timedelta

from pydantic import BaseModel, Field, validator

__all__ = ["Event"]


class Event(BaseModel):
    priority: int = Field(
        ...,
        title="Priority",
        description="The importance of the mission event",
        ge=1,
        le=5,
    )
    mission_time: timedelta = Field(
        ...,
        title="Mission Time",
        description="The time this event starts at, relative to the start of the mission",
    )

    @validator("mission_time")
    def non_negative_time(cls, v):
        assert v >= timedelta(0)
        return v
