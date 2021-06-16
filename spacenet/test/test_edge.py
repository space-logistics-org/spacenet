import unittest

import pytest
from pydantic import ValidationError
from spacenet.schemas.edge import SurfaceEdge, SpaceEdge, FlightEdge

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
