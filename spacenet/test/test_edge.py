import json
import unittest

import pkg_resources
import pytest
from pydantic import ValidationError

from spacenet import test
from spacenet.schemas import edge as eos
from spacenet.schemas.edge import EdgeType, FlightEdge, SpaceEdge, SurfaceEdge
from .lunar_sortie_utils import edges

pytestmark = [pytest.mark.unit, pytest.mark.edge, pytest.mark.schema]


class TestEdge(unittest.TestCase):
    def testSurEdge(self):
        goodData = {
            "name": "FL-GA",
            "id": 1,
            "description": "Surface Edge from Florida to Georgia",
            "type": "Surface",
            "origin_id": 1,
            "destination_id": 2,
            "distance": 100,
        }
        badTypeData = {
            "name": "FL-GA",
            "id": 1,
            "description": "Surface Edge from Florida to Georgia",
            "type": "orbital",
            "origin_id": 1,
            "destination_id": 2,
            "distance": 100,
        }
        badDistanceData = {
            "name": "FL-GA",
            "id": 1,
            "description": "Surface Edge from Florida to Georgia",
            "type": "Surface",
            "origin_id": 1,
            "destination_id": 2,
            "distance": -100,
        }
        badIDData = {
            "name": "FL-GA",
            "id": 1,
            "description": "Surface Edge from Florida to Georgia",
            "type": "Surface",
            "origin_id": "",
            "destination_id": 2,
            "distance": 100,
        }
        goodEdge = SurfaceEdge.parse_obj(goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.distance, goodData.get("distance"))

        with self.assertRaises(ValidationError):
            badTypeEdge = SurfaceEdge.parse_obj(badTypeData)

        with self.assertRaises(ValidationError):
            badDistanceEdge = SurfaceEdge.parse_obj(badDistanceData)

        with self.assertRaises(ValidationError):
            badIDEdge = SurfaceEdge.parse_obj(badIDData)

    def testSpaEdge(self):
        goodData = {
            "name": "Earth-Moon",
            "id": 1,
            "description": "Space edge from Earth to the moon",
            "type": "Space",
            "origin_id": 1,
            "destination_id": 2,
            "duration": 100,
        }
        badDurationData = {
            "name": "Earth-Moon",
            "id": 1,
            "description": "Space edge from Earth to the moon",
            "type": "Space",
            "origin_id": 1,
            "destination_id": 2,
            "duration": -100,
        }
        goodEdge = SpaceEdge.parse_obj(goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.duration, goodData.get("duration"))

        with self.assertRaises(ValidationError):
            badDurationEdge = SurfaceEdge.parse_obj(badDurationData)

    def testFltEdge(self):
        goodData = {
            "name": "Earth-Moon",
            "id": 1,
            "description": "Flight edge from Earth to the moon",
            "type": "Flight",
            "origin_id": 1,
            "destination_id": 2,
            "duration": 100,
            "max_crew": 10,
            "max_cargo": 10,
        }
        badMax_crewData = {
            "name": "Earth-Moon",
            "id": 1,
            "description": "Flight edge from Earth to the moon",
            "type": "Flight",
            "origin_id": 1,
            "destination_id": 2,
            "duration": 100,
            "max_crew": -10,
            "max_cargo": 10,
        }
        badMax_cargoData = {
            "name": "Earth-Moon",
            "id": 1,
            "description": "Flight edge from Earth to the moon",
            "type": "Flight",
            "origin_id": 1,
            "destination_id": 2,
            "duration": 100,
            "max_crew": 10,
            "max_cargo": -10,
        }
        goodEdge = FlightEdge.parse_obj(goodData)
        self.assertEqual(goodEdge.name, goodData.get("name"))
        self.assertEqual(goodEdge.description, goodData.get("description"))
        self.assertEqual(goodEdge.type, goodData.get("type"))
        self.assertEqual(goodEdge.origin_id, goodData.get("origin_id"))
        self.assertEqual(goodEdge.destination_id, goodData.get("destination_id"))
        self.assertEqual(goodEdge.max_crew, goodData.get("max_crew"))
        self.assertEqual(goodEdge.max_cargo, goodData.get("max_cargo"))

        with self.assertRaises(ValidationError):
            badMax_crewEdge = FlightEdge.parse_obj(badMax_crewData)

        with self.assertRaises(ValidationError):
            badMax_cargoEdge = FlightEdge.parse_obj(badMax_cargoData)


class TestFromFile(unittest.TestCase):

    good_edges = json.loads(
        pkg_resources.resource_string(test.__name__, "good_edges.json")
    )

    good_surface = list(
        filter(lambda edge: edge["type"] == EdgeType.Surface.value, good_edges)
    )
    good_space = list(
        filter(lambda edge: edge["type"] == EdgeType.Space.value, good_edges)
    )
    good_flight = list(
        filter(lambda edge: edge["type"] == EdgeType.Flight.value, good_edges)
    )

    bad_edges = json.loads(
        pkg_resources.resource_string(test.__name__, "bad_edges.json")
    )

    def test_FlightEdge(self):

        for edge in self.good_flight:

            testedge = eos.FlightEdge.parse_obj(edge)
            self.assertEqual(testedge.name, edge.get("name"))
            self.assertEqual(testedge.origin_id, edge.get("origin_id"))
            self.assertEqual(testedge.destination_id, edge.get("destination_id"))
            self.assertEqual(testedge.duration, edge.get("duration"))
            self.assertEqual(testedge.max_crew, edge.get("max_crew"))
            self.assertEqual(testedge.max_cargo, edge.get("max_cargo"))
            self.assertEqual(testedge.description, edge.get("description"))

    def test_SpaceEdge(self):

        for edge in self.good_space:

            testedge = eos.SpaceEdge.parse_obj(edge)
            self.assertEqual(testedge.name, edge.get("name"))
            self.assertEqual(testedge.origin_id, edge.get("origin_id"))
            self.assertEqual(testedge.destination_id, edge.get("destination_id"))
            self.assertEqual(testedge.duration, edge.get("duration"))
            self.assertEqual(testedge.description, edge.get("description"))

    def test_SurfaceEdge(self):

        for edge in self.good_surface:

            testedge = eos.SurfaceEdge.parse_obj(edge)
            self.assertEqual(testedge.name, edge.get("name"))
            self.assertEqual(testedge.origin_id, edge.get("origin_id"))
            self.assertEqual(testedge.destination_id, edge.get("destination_id"))
            self.assertEqual(testedge.distance, edge.get("distance"))
            self.assertEqual(testedge.description, edge.get("description"))

    def test_BadFlightEdge(self):
        for edge in self.bad_edges:
            with self.assertRaises(ValidationError):
                bad_edge = eos.FlightEdge.parse_obj(edge)

    def test_BadSurfaceEdge(self):
        for edge in self.bad_edges:
            with self.assertRaises(ValidationError):
                bad_edge = eos.SurfaceEdge.parse_obj(edge)

    def test_BadSpaceEdge(self):
        for edge in self.bad_edges:
            with self.assertRaises(ValidationError):
                bad_edge = eos.SpaceEdge.parse_obj(edge)


@pytest.mark.lunar_sortie
def test_lunar_sortie_edges(edges):
    for edge_obj in edges:
        edge = SpaceEdge.parse_obj(edge_obj)
        for attr, value in edge_obj.items():
            assert value == getattr(edge, attr)
