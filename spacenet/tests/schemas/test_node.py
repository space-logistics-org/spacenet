"""
This module contains tests for nodes.
"""
import json
import unittest

import pkg_resources
import pytest
from pydantic import ValidationError

from spacenet.schemas import node as nos, test
from spacenet.schemas.node import LagrangeNode, NodeType, OrbitalNode, SurfaceNode

pytestmark = [pytest.mark.unit, pytest.mark.node, pytest.mark.schema]


class TestNode(unittest.TestCase):
    def testSurNode(self):
        goodData = {
            "name": "KSC",
            "description": "Kennedy Space Center",
            "type": "SurfaceNode",
            "body_1": "Earth",
            "latitude": 28.57,
            "longitude": -80.65,
        }
        badData = {
            "name": "KSC",
            "description": "Kennedy Space Center",
            "type": "OrbitalNode",
            "body_1": "Earth",
            "latitude": 28.57,
            "longitude": -80.65,
        }
        goodNode = SurfaceNode.parse_obj(goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.type, goodData.get("type"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.latitude, goodData.get("latitude"))
        self.assertEqual(goodNode.longitude, goodData.get("longitude"))

        with self.assertRaises(ValidationError):
            badNode = SurfaceNode.parse_obj(badData)

    def testOrbNode(self):
        goodData = {
            "name": "LEO",
            "description": "Low Earth Orbit",
            "body_1": "Earth",
            "apoapsis": 296,
            "periapsis": 296,
            "inclination": 28.5,
            "type": "OrbitalNode",
        }
        badData = {
            "name": "LEO",
            "description": "Low Earth Orbit",
            "body_1": "Saturn",
            "apoapsis": -100,
            "periapsis": -100,
            "inclination": -100,
            "type": "OrbitalNode",
        }
        goodNode = OrbitalNode.parse_obj(goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.apoapsis, goodData.get("apoapsis"))
        self.assertEqual(goodNode.periapsis, goodData.get("periapsis"))
        self.assertEqual(goodNode.inclination, goodData.get("inclination"))

        with self.assertRaises(ValidationError):
            badNode = OrbitalNode.parse_obj(badData)

    def testLagNode(self):
        goodData = {
            "name": "EM L5",
            "description": "Earth-Moon Lagrange point 5",
            "body_1": "Earth",
            "body_2": "Moon",
            "lp_number": 5,
            "type": "LagrangeNode",
        }
        badData = {
            "name": "LEO",
            "description": "Low Earth Orbit",
            "body_1": "Saturn",
            "apoapsis": -100,
            "periapsis": -100,
            "body_2": "Titan",
            "lp_number": 6,
            "type": "LagrangeNode",
        }
        goodNode = LagrangeNode.parse_obj(goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.body_2, goodData.get("body_2"))
        self.assertEqual(goodNode.lp_number, goodData.get("lp_number"))

        with self.assertRaises(ValidationError):
            badNode = LagrangeNode.parse_obj(badData)


class TestFromFile(unittest.TestCase):
    good_nodes = json.loads(
        pkg_resources.resource_string(test.__name__, "good_nodes.json")
    )

    good_orbital = list(
        filter(lambda node: node["type"] == NodeType.Orbital.value, good_nodes)
    )
    good_surface = list(
        filter(lambda node: node["type"] == NodeType.Surface.value, good_nodes)
    )
    good_lagrange = list(
        filter(lambda node: node["type"] == NodeType.Lagrange.value, good_nodes)
    )

    bad_nodes = json.loads(
        pkg_resources.resource_string(test.__name__, "bad_nodes.json")
    )

    def test_OrbitalNode(self):

        for node in self.good_orbital:

            testnode = nos.OrbitalNode.parse_obj(node)
            self.assertEqual(testnode.name, node.get("name"))
            self.assertEqual(testnode.description, node.get("description"))
            self.assertEqual(testnode.body_1, node.get("body_1"))
            self.assertEqual(testnode.type, node.get("type"))
            self.assertEqual(testnode.apoapsis, node.get("apoapsis"))
            self.assertEqual(testnode.periapsis, node.get("periapsis"))
            self.assertEqual(testnode.inclination, node.get("inclination"))

    def test_SurfaceNode(self):

        for node in self.good_surface:

            testnode = nos.SurfaceNode.parse_obj(node)
            self.assertEqual(testnode.name, node.get("name"))
            self.assertEqual(testnode.description, node.get("description"))
            self.assertEqual(testnode.body_1, node.get("body_1"))
            self.assertEqual(testnode.type, node.get("type"))
            self.assertEqual(testnode.latitude, node.get("latitude"))
            self.assertEqual(testnode.longitude, node.get("longitude"))

    def test_LagrangeNode(self):

        for node in self.good_lagrange:

            testnode = nos.LagrangeNode.parse_obj(node)
            self.assertEqual(testnode.name, node.get("name"))
            self.assertEqual(testnode.description, node.get("description"))
            self.assertEqual(testnode.body_1, node.get("body_1"))
            self.assertEqual(testnode.type, node.get("type"))
            self.assertEqual(testnode.body_2, node.get("body_2"))
            self.assertEqual(testnode.lp_number, node.get("lp_number"))

    def test_BadOrbitalNode(self):
        for node in self.bad_nodes:
            with self.assertRaises(ValidationError):
                bad_node = nos.OrbitalNode.parse_obj(node)

    def test_BadSurfaceNode(self):
        for node in self.bad_nodes:
            with self.assertRaises(ValidationError):
                bad_node = nos.OrbitalNode.parse_obj(node)

    def test_BadLagrangeNode(self):
        for node in self.bad_nodes:
            with self.assertRaises(ValidationError):
                bad_node = nos.OrbitalNode.parse_obj(node)
