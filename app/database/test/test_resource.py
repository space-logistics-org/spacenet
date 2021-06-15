import unittest
import json
import pkg_resources

from spacenet import test

from app.database.api.models import resource as models
from app.database.api.schemas import resource as schemas
from app.database.api.database import SessionLocal, Base, engine

class TestResource(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_example_data(self):
        resource_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'resource_data.json'
            )
        )
        db = SessionLocal()
        try:
            for resource in resource_data:
                if resource["type"] == "Continuous":
                    resource = schemas.ContinuousResourceCreate.parse_obj(resource)
                    db_resource = models.ContinuousResource(**resource_dict())
                    self.assertIsNone(db_resource.id)
                    db.add(db_resource)
                    db.commit()
                    db.refresh(db_resource)
                    self.assertIsNotNone(db_resource.id)
                    db.delete(db_resource)
                    db.commit()

                elif resource["type"] == "Discrete":
                    resource = schemas.DiscreteResourceCreate.parse_obj(resource)
                    db_resource = models.DiscreteResource(**resource_dict())
                    self.assertIsNone(db_resource.id)
                    db.add(db_resource)
                    db.commit()
                    db.refresh(db_resource)
                    self.assertIsNotNone(db_resource.id)
                    db.delete(db_resource)
                    db.commit()
        finally:
            db.close()
