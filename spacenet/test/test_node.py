import pytest

from spacenet.schemas.node import LagrangeNode, OrbitalNode, SurfaceNode

import unittest
import json
import pkg_resources
from pydantic import ValidationError

from spacenet.schemas import node as nos
from spacenet import test

pytestmark = [pytest.mark.unit, pytest.mark.node]


class TestNode(unittest.TestCase):
    def testSurNode(self):
        goodData = {"name": "KSC", "description": "Kennedy Space Center", "type": "Surface",
                    "body_1": "Earth", "latitude": 28.57, "longitude": -80.65
                    }
        badData = {"name": "KSC", "description": "Kennedy Space Center", "type": "Orbital",
                   "body_1": "Earth", "latitude": 28.57, "longitude": -80.65
                   }
        goodNode = SurfaceNode(**goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.type, goodData.get("type"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.latitude, goodData.get("latitude"))
        self.assertEqual(goodNode.longitude, goodData.get("longitude"))

        with self.assertRaises(ValidationError):
            badNode = SurfaceNode(**badData)

    def testOrbNode(self):
        goodData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Earth",
                    "apoapsis": 296, "periapsis": 296, "inclination": 28.5, "type": "Orbital"
                    }
        badData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Saturn",
                   "apoapsis": -100, "periapsis": -100, "inclination": -100, "type": "Orbital"
                   }
        goodNode = OrbitalNode(**goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.apoapsis, goodData.get("apoapsis"))
        self.assertEqual(goodNode.periapsis, goodData.get("periapsis"))
        self.assertEqual(goodNode.inclination, goodData.get("inclination"))

        with self.assertRaises(ValidationError):
            badNode = OrbitalNode(**badData)

    def testLagNode(self):
        goodData = {"name": "EM L5", "description": "Earth-Moon Lagrange point 5",
                    "body_1": "Earth", "body_2": "Moon", "lp_number": 5, "type": "Lagrange"
                    }
        badData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Saturn",
                   "apoapsis": -100, "periapsis": -100, "body_2": "Titan", "lp_number": 6,
                   "type": "Lagrange"
                   }
        goodNode = LagrangeNode(**goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.body_2, goodData.get("body_2"))
        self.assertEqual(goodNode.lp_number, goodData.get("lp_number"))

        with self.assertRaises(ValidationError):
            badNode = LagrangeNode(**badData)


class TestingData(unittest.TestCase):

    def test_OrbitalNode(self):

        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_nodes.json'
            )
        )

        for nodes in nodes_data:

            if nodes["type"] == "Orbital":
                testnode = nos.OrbitalNode(**nodes)
                self.assertEqual(testnode.name, nodes.get("name"))
                self.assertEqual(testnode.description, nodes.get("description"))
                self.assertEqual(testnode.body_1, nodes.get("body_1"))
                self.assertEqual(testnode.type, nodes.get("type"))
                self.assertEqual(testnode.apoapsis, nodes.get("apoapsis"))
                self.assertEqual(testnode.periapsis, nodes.get("periapsis"))
                self.assertEqual(testnode.inclination, nodes.get("inclination"))

    def test_SurfaceNode(self):

        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_nodes.json'
            )
        )

        for nodes in nodes_data:

            if nodes["type"] == "Surface":
                testnode = nos.SurfaceNode(**nodes)
                self.assertEqual(testnode.name, nodes.get("name"))
                self.assertEqual(testnode.description, nodes.get("description"))
                self.assertEqual(testnode.body_1, nodes.get("body_1"))
                self.assertEqual(testnode.type, nodes.get("type"))
                self.assertEqual(testnode.latitude, nodes.get("latitude"))
                self.assertEqual(testnode.longitude, nodes.get("longitude"))

    def test_LagrangeNode(self):

        nodes_data = json.loads(
            pkg_resources.resource_string(
                test.__name__,
                'good_nodes.json'
            )
        )

        for nodes in nodes_data:

            if nodes["type"] == "Lagrange":
                testnode = nos.LagrangeNode(**nodes)
                self.assertEqual(testnode.name, nodes.get("name"))
                self.assertEqual(testnode.description, nodes.get("description"))
                self.assertEqual(testnode.body_1, nodes.get("body_1"))
                self.assertEqual(testnode.type, nodes.get("type"))
                self.assertEqual(testnode.body_2, nodes.get("body_2"))
                self.assertEqual(testnode.lp_number, nodes.get("lp_number"))

    def test_BadOrbitalNode(self):
        node = {"type": "Orbtial", "name": "test", "body_1": "Mars", "apoapsis": 10000,
                "periapsis": "3000", "inclination": 70,
                "description": "String is not valid periapsis"
                }
        with self.assertRaises(ValidationError):
            bad_node = nos.OrbitalNode(**node)

    def test_BadSurfaceNode(self):
        node = {"type": "Surface", "name": "Test1", "body_1": "Earth", "latitude": True,
                "longitude": True, "description": "True is not valid Long/Lat"
                }
        with self.assertRaises(ValidationError):
            bad_node = nos.OrbitalNode(**node)

    def test_BadLagrangeNode(self):
        node = {"type": "Lagrange", "name": "Test5", "body_1": "Mars", "body_2": "Sun",
                "lp_number": 6, "description": "6 is not valid LP number"
                }
        with self.assertRaises(ValidationError):
            bad_node = nos.LagrangeNode(**node)
