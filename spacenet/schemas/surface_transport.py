from pydantic import BaseModel, Field, PositiveInt, PositiveFloat
from typing import List 


class SurfaceTransport(BaseModel):

    # Schema for Surface Transport

    name: str = Field(..., title = "Name", description = "The surface transport name")

    origin_node_id: PositiveInt = Field(..., title = "Origin Node ID", description = "The ID of the surface transport's origin node")
    
    destination_node_id: PositiveInt = Field(..., title = "Destination Node ID", description = "The ID of the surface transport's destination node")

    time: PositiveFloat = Field(..., title = "Time", description = "The execution time")

    priority: int = Field(..., title = "Priority", description = "The importance of the mission event", ge = 1, le = 5)

    elements_id_list: List[PositiveInt] = Field(..., title = "List of Element IDs", description = "The list of IDs of elements being transported")
