from datetime import datetime
from typing import Any, List, Set

from pydantic import BaseModel

from .mission_demand_model import MissionDemand


class Mission(BaseModel):
    name: str
    start_date: datetime
    events: List[Any]
    demand_models: Set[MissionDemand]
    origin: int
    destination: int
    return_origin: int
    return_destination: int


