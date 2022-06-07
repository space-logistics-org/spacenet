import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from ..api.utilities import set_sqlite_foreign_key_pragma

TEST_DB_URL = "sqlite:///./test.db"

test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

event.listens_for(Engine, "connect")(set_sqlite_foreign_key_pragma)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db():
    database = TestingSessionLocal()
    yield database
    database.close()
