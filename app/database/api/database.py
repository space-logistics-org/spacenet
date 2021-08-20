"""
This module defines a database engine and a function for retrieving a session which uses that
engine.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from .utilities import set_sqlite_foreign_key_pragma

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

event.listens_for(Engine, "connect")(set_sqlite_foreign_key_pragma)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    """
    A generator which provides a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
