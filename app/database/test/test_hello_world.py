import unittest
import json
import pkg_resources
import pytest

from spacenet import test

from app.database.api.models import hello_world as models
from app.database.api.schemas import hello_world as schemas
from app.database.api.database import Base, engine
from .utilities import TestingSessionLocal

pytestmark = [pytest.mark.unit, pytest.mark.database]


class TestHelloWorld(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_example_data(self):
        messages = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'hello_world_data.json'
            )
        )
        for message in messages.get('good_data'):
            hello = schemas.HelloWorldCreate.parse_obj(message)
            db_hello = models.HelloWorld(**hello.dict())
            self.assertIsNone(db_hello.id)
            self.db.add(db_hello)
            self.db.commit()
            self.db.refresh(db_hello)
            self.assertIsNotNone(db_hello.id)
            self.db.delete(db_hello)
            self.db.commit()
