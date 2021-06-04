from sqlalchemy import Column, Integer, String

from ..database import Base

class HelloWorld(Base):
    __tablename__ = "hello"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
