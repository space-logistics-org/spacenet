from pydantic import BaseModel, Field

__all__ = ["Event"]


class Event(BaseModel):
    priority: int = Field(
        ...,
        title="Priority",
        description="The importance of the mission event",
        ge=1,
        le=5,
    )
