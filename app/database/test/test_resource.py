import unittest
import json
import pkg_resources
import pytest

from spacenet.schemas import test

from app.database.api.models import resource as models
from app.database.api.schemas import resource as schemas
from app.database.api.database import Base, engine
from .utilities import TestingSessionLocal

pytestmark = [pytest.mark.unit, pytest.mark.resource, pytest.mark.database]


class TestResource(unittest.TestCase):
    resource_data = json.loads(
        pkg_resources.resource_string(
            test.__name__,
            'resource_data.json'
        )
    )

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_example_data(self):

        db = self.db
        for resource in self.resource_data:
            if resource["type"] == "Continuous":
                resource = schemas.ContinuousResource.parse_obj(resource)
                resource_dict = resource.dict()
                db_resource = models.ContinuousResource(**resource_dict)
                self.assertIsNone(db_resource.id)
                db.add(db_resource)
                db.commit()
                db.refresh(db_resource)
                self.assertIsNotNone(db_resource.id)
                db.delete(db_resource)
                db.commit()

            elif resource["type"] == "Discrete":
                resource = schemas.DiscreteResource.parse_obj(resource)
                resource_dict = resource.dict()
                db_resource = models.DiscreteResource(**resource_dict)
                self.assertIsNone(db_resource.id)
                db.add(db_resource)
                db.commit()
                db.refresh(db_resource)
                self.assertIsNotNone(db_resource.id)
                db.delete(db_resource)
                db.commit()
