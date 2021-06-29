from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database.api.database import Base

__all__ = [
    "State"
]


class State(Base):
    __tablename__ = "State"

    id = Column(Integer, primary_key=True, index=True)
    element_id = Column(Integer, ForeignKey("Elements.id"), nullable=False)
    name = Column(String)
    state_type = Column(String)
    is_initial_state = Column(Boolean)
