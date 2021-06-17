import unittest
import json
import pkg_resources
import pytest

from spacenet import test

from app.database.api.models import edge as models
from app.database.api.schemas import edge as schemas
from app.database.api.database import Base, engine
from .utilities import TestingSessionLocal

pytestmark = [pytest.mark.unit, pytest.mark.edge]


class TestEdgeData(unittest.TestCase):

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_edges(self):
        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_edges.json'
            )
        )

        for edge in edge_data:
            if edge["type"] == "Surface":
                testedge = schemas.SurfaceEdgeCreate.parse_obj(edge)
                db_edge = models.SurfaceEdge(**testedge.dict())
                self.assertIsNone(db_edge.id)
                self.db.add(db_edge)
                self.db.commit()
                self.db.refresh(db_edge)
                self.assertIsNotNone(db_edge.id)
                self.assertIsNotNone(db_edge.name)
                self.assertIsNotNone(db_edge.origin_id)
                self.assertIsNotNone(db_edge.destination_id)
                self.assertIsNotNone(db_edge.distance)
                self.assertIsNotNone(db_edge.description)
                self.db.delete(db_edge)
                self.db.commit()

            elif edge["type"] == "Space":
                testedge = schemas.SpaceEdgeCreate.parse_obj(edge)
                db_edge = models.SpaceEdge(**testedge.dict())
                self.assertIsNone(db_edge.id)
                self.db.add(db_edge)
                self.db.commit()
                self.db.refresh(db_edge)
                self.assertIsNotNone(db_edge.id)
                self.assertIsNotNone(db_edge.name)
                self.assertIsNotNone(db_edge.origin_id)
                self.assertIsNotNone(db_edge.destination_id)
                self.assertIsNotNone(db_edge.duration)
                self.assertIsNotNone(db_edge.description)
                self.db.delete(db_edge)
                self.db.delete(db_edge)
                self.db.commit()

            elif edge["type"] == "Flight":
                testedge = schemas.FlightEdgeCreate.parse_obj(edge)
                db_edge = models.FlightEdge(**testedge.dict())
                self.assertIsNone(db_edge.id)
                print(db_edge.__dict__)
                self.db.add(db_edge)
                self.db.commit()
                self.db.refresh(db_edge)
                self.assertIsNotNone(db_edge.id)
                self.assertIsNotNone(db_edge.name)
                self.assertIsNotNone(db_edge.origin_id)
                self.assertIsNotNone(db_edge.destination_id)
                self.assertIsNotNone(db_edge.duration)
                self.assertIsNotNone(db_edge.max_crew)
                self.assertIsNotNone(db_edge.max_cargo)
                self.assertIsNotNone(db_edge.description)
                self.db.delete(db_edge)
                self.db.commit()

# To test, run : python -m unittest app.database.test.test_edgeDatabaseModel