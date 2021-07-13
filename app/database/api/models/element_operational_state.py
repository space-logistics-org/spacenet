from sqlalchemy import Column, Integer, String, Float, Boolean
from sortedcontainers import SortedSet

from ..database import Base
from  spacenet.schemas.state import stateType

__all__ = ["StateType", "state"]

class StateModel(Base):
    __tablename__ = "State Models"

    type = Column(String)
    demandModels = Column(SortedSet)
