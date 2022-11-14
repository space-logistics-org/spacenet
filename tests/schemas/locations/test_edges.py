import unittest
from uuid import uuid4
from datetime import timedelta

from spacenet.schemas import SurfaceNode, OrbitalNode, SurfaceEdge, SpaceEdge, FlightEdge

class TestSurfaceEdge(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test edge",
            "origin": uuid4(),
            "destination": uuid4(),
            "distance": 100e3
        }
        self.test_edge = SurfaceEdge(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_edge.name, self.test_data.get("name"))
        self.assertEqual(self.test_edge.origin, self.test_data.get("origin"))
        self.assertEqual(self.test_edge.destination, self.test_data.get("destination"))
        self.assertEqual(self.test_edge.distance, self.test_data.get("distance"))

class TestSpaceEdge(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test edge",
            "origin": uuid4(),
            "destination": uuid4(),
            "duration": timedelta(hours=1)
        }
        self.test_edge = SpaceEdge(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_edge.name, self.test_data.get("name"))
        self.assertEqual(self.test_edge.origin, self.test_data.get("origin"))
        self.assertEqual(self.test_edge.destination, self.test_data.get("destination"))
        self.assertEqual(self.test_edge.duration, self.test_data.get("duration"))

class TestFlightEdge(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test edge",
            "origin": uuid4(),
            "destination": uuid4(),
            "duration": timedelta(hours=1),
            "max_crew": 1,
            "max_cargo": 100
        }
        self.test_edge = FlightEdge(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_edge.name, self.test_data.get("name"))
        self.assertEqual(self.test_edge.origin, self.test_data.get("origin"))
        self.assertEqual(self.test_edge.destination, self.test_data.get("destination"))
        self.assertEqual(self.test_edge.duration, self.test_data.get("duration"))
        self.assertEqual(self.test_edge.max_crew, self.test_data.get("max_crew"))
        self.assertEqual(self.test_edge.max_cargo, self.test_data.get("max_cargo"))


