import unittest
import json
import pkg_resources

from spacenet import test

from app.database.api.models import hello_world as models
from app.database.api.schemas import hello_world as schemas
from app.database.api.database import SessionLocal

class TestHelloWorld(unittest.TestCase):
    def test_model_good_example_data(self):
        messages = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'hello_world_data.json'
            )
        )
        db = SessionLocal()
        try:
            for message in messages.get('good_data'):
                hello = schemas.HelloWorldCreate.parse_obj(message)
                db_hello = models.HelloWorld(**hello.dict())
                self.assertIsNone(db_hello.id)
                db.add(db_hello)
                db.commit()
                db.refresh(db_hello)
                self.assertIsNotNone(db_hello.id)
                db.delete(db_hello)
                db.commit()
        finally:
            db.close()
