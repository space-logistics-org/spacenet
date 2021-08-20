"""
This module defines the database schema for state.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database.api.database import Base

__all__ = ["State"]


class State(Base):
    """
    A row representing a single operational state of an element.
    """
    __tablename__ = "state"

    id = Column(Integer, primary_key=True, index=True)
    element_id = Column(
        Integer, ForeignKey("element.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String)
    state_type = Column(String)
    is_initial_state = Column(Boolean)
    element = relationship("Element", back_populates="states")
