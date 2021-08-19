"""
This module runs regression tests for the edge database schema. The file imports a json file containing mock edge data to use for the testing.
"""

import unittest
import json
import pkg_resources
import pytest

from spacenet.schemas import test

from app.database.api.models import edge as models
from app.database.api.schemas import edge as schemas
from app.database.api.database import Base, engine
from spacenet.schemas import EdgeType
from .utilities import TestingSessionLocal

pytestmark = [pytest.mark.unit, pytest.mark.edge, pytest.mark.database]


class TestEdgeData(unittest.TestCase):
    edge_data = json.loads(
        pkg_resources.resource_string(
            test.__name__,
            'good_edges.json'
        )
    )

    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_model_good_edges(self):

        for edge in self.edge_data:
            if edge["type"] == EdgeType.Surface.value:
                testedge = schemas.SurfaceEdge.parse_obj(edge)
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

            elif edge["type"] == EdgeType.Space.value:
                testedge = schemas.SpaceEdge.parse_obj(edge)
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

            elif edge["type"] == EdgeType.Flight.value:
                testedge = schemas.FlightEdge.parse_obj(edge)
                db_edge = models.FlightEdge(**testedge.dict())
                self.assertIsNone(db_edge.id)
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
