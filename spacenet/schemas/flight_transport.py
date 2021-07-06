from pydantic import BaseModel, Field, PositiveFloat



class FlightTransport(BaseModel):

    # Schema for Flight Transport

    name: str = Field(..., title = "Name", description = "The flight transport name")

    node: str = Field(..., title = "Node", description = "The origin of the flight transport")

    time: PositiveFloat = Field(..., title = "Time", description = "The execution time")

    priority: int = Field(..., title = "Priority", description = "The importance of the mission event", ge = 1, le = 5)

    trajectory: str = Field(..., title = "Trajectory", description = "The nodes that the vehicle will travel to and from")

    elements: str = Field(..., title = "Elements", description = "The elements")
