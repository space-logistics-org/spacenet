from sqlalchemy import Column, Integer, String, Float, Boolean

from ..database import Base
from spacenet.schemas.state import StateType

__all__ = ["StateType"]


class StateModel(Base):
    __tablename__ = "State Models"

    id = Column(Integer, primary_key=True)
    type = Column(String)
    # demandModels = Column(SortedSet)
    # TODO: cannot have a column of sets, use a foreign key relation into tables which
    #  contain the sets
