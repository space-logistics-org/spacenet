import json
import unittest

import pkg_resources
import pytest
from pydantic import ValidationError

from spacenet import test
from spacenet.schemas import edge as eos
from spacenet.schemas.edge import FlightEdge, SpaceEdge, SurfaceEdge

pytestmark = [pytest.mark.unit, pytest.mark.edge]


class TestEdge(unittest.TestCase):

    def testSurEdge(self):
        goodData = {"name": "FL-GA", "id": 1, "description": "Surface Edge from Florida to Georgia", "type": "Surface", "origin_id": 1, "destination_id": 2, "distance": 100}
        badTypeData = {"name": "FL-GA", "id": 1, "description": "Surface Edge from Florida to Georgia", "type": "orbital", "origin_id": 1, "destination_id": 2, "distance": 100}
        badDistanceData = {"name": "FL-GA", "id": 1, "description": "Surface Edge from Florida to Georgia", "type": "Surface", "origin_id": 1, "destination_id": 2, "distance": -100}
        badIDData = {"name": "FL-GA", "id": 1, "description": "Surface Edge from Florida to Georgia", "type": "Surface", "origin_id": "", "destination_id": 2, "distance": 100}
        goodEdge = SurfaceEdge(**goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.distance, goodData.get("distance"))

        with self.assertRaises(ValidationError):
            badTypeEdge = SurfaceEdge(**badTypeData)

        with self.assertRaises(ValidationError):
            badDistanceEdge = SurfaceEdge(**badDistanceData)

        with self.assertRaises(ValidationError):
            badIDEdge = SurfaceEdge(**badIDData)

    def testSpaEdge(self):
        goodData = {"name": "Earth-Moon", "id": 1, "description": "Space edge from Earth to the moon", "type": "Space", "origin_id": 1, "destination_id": 2, "duration": 100}
        badDurationData = {"name": "Earth-Moon", "id": 1, "description": "Space edge from Earth to the moon", "type": "Space", "origin_id": 1, "destination_id": 2, "duration": -100}
        goodEdge = SpaceEdge(**goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.duration, goodData.get("duration"))

        with self.assertRaises(ValidationError):
            badDurationEdge = SurfaceEdge(**badDurationData)

    def testFltEdge(self):
        goodData = {"name": "Earth-Moon", "id": 1, "description": "Flight edge from Earth to the moon", "type": "Flight", "origin_id": 1, "destination_id": 2, "duration": 100, "max_crew": 10, "max_cargo": 10}
        badMax_crewData = {"name": "Earth-Moon", "id": 1, "description": "Flight edge from Earth to the moon", "type": "Flight", "origin_id": 1, "destination_id": 2, "duration": 100, "max_crew": -10, "max_cargo": 10}
        badMax_cargoData = {"name": "Earth-Moon", "id": 1, "description": "Flight edge from Earth to the moon", "type": "Flight", "origin_id": 1, "destination_id": 2, "duration": 100, "max_crew": 10, "max_cargo": -10}
        goodEdge = FlightEdge(**goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.max_crew, goodData.get("max_crew"))
        self.assertEqual(goodEdge.max_cargo, goodData.get("max_cargo"))

        with self.assertRaises(ValidationError):
            badMax_crewEdge = FlightEdge(**badMax_crewData)

        with self.assertRaises(ValidationError):
            badMax_cargoEdge = FlightEdge(**badMax_cargoData)


class TestingData(unittest.TestCase):

    def test_FlightEdge(self):

        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_edges.json'
            )
        )

        for edge in edge_data:

            if edge["type"] == "Flight":
                testedge = eos.FlightEdge(**edge)
                self.assertEqual(testedge.name, edge.get("name"))
                self.assertEqual(testedge.origin_id, edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.duration, edge.get("duration"))
                self.assertEqual(testedge.max_crew, edge.get("max_crew"))
                self.assertEqual(testedge.max_cargo, edge.get("max_cargo"))
                self.assertEqual(testedge.description, edge.get("description"))

    def test_SpaceEdge(self):

        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_edges.json'
            )
        )

        for edge in edge_data:

            if edge["type"] == "Space":
                testedge = eos.SpaceEdge(**edge)
                self.assertEqual(testedge.name, edge.get("name"))
                self.assertEqual(testedge.origin_id, edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.duration, edge.get("duration"))
                self.assertEqual(testedge.description, edge.get("description"))

    def test_SurfaceEdge(self):

        edge_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_edges.json'
            )
        )

        for edge in edge_data:

            if edge["type"] == "Surface":
                testedge = eos.SurfaceEdge(**edge)
                self.assertEqual(testedge.name, edge.get("name"))
                self.assertEqual(testedge.origin_id, edge.get("origin_id"))
                self.assertEqual(testedge.destination_id, edge.get("destination_id"))
                self.assertEqual(testedge.distance, edge.get("distance"))
                self.assertEqual(testedge.description, edge.get("description"))

    def test_BadFlightEdge(self):
        edge = {"type": "Flight", "name": "Test1", "origin_id": 1, "destination_id": 2,
                "duration": 25, "max_crew": 6, "max_cargo": -100,
                "description": "Invalid max_cargo input."
                }
        with self.assertRaises(ValidationError):
            bad_edge = eos.FlightEdge(**edge)

    def test_BadSurfaceEdge(self):
        edge = {"type": "Space", "name": "Test3", "origin_id": 3, "destination_id": 2.5,
                "duration": 25, "description": "Invalid destination_id input."
                }
        with self.assertRaises(ValidationError):
            bad_edge = eos.SurfaceEdge(**edge)

    def test_BadSpaceEdge(self):
        edge = {"type": "Surface", "name": "Test5", "origin_id": 5, "destination_id": 2,
                "description": "Invalid distance type."
                }
        with self.assertRaises(ValidationError):
            bad_edge = eos.SpaceEdge(**edge)
