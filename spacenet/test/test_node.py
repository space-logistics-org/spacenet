import unittest

import pytest
from pydantic import ValidationError
from spacenet.schemas.node import SurfaceNode, OrbitalNode, LagrangeNode

pytestmark = [pytest.mark.unit, pytest.mark.node]


class TestNode(unittest.TestCase):
    def testSurNode(self):
        goodData = { "name": "KSC", "description": "Kennedy Space Center", "type": "Surface", "body_1": "Earth", "latitude": 28.57, "longitude": -80.65}
        badData = {"name": "KSC", "description": "Kennedy Space Center", "type": "Orbital", "body_1": "Earth", "latitude": 28.57, "longitude": -80.65}
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
        goodData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Earth", "apoapsis": 296, "periapsis": 296, "inclination": 28.5}
        badData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Saturn", "apoapsis": -100, "periapsis": -100, "inclination": -100}
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
        goodData = {"name": "EM L5", "description": "Earth-Moon Lagrange point 5", "body_1": "Earth", "body_2": "Moon", "lp_number": 5}
        badData = {"name": "LEO", "description": "Low Earth Orbit", "body_1": "Saturn", "apoapsis": -100, "periapsis": -100, "body_2": "Titan", "lp_number": 6}
        goodNode = LagrangeNode(**goodData)
        self.assertEqual(goodNode.name, goodData.get("name"))
        self.assertEqual(goodNode.description, goodData.get("description"))
        self.assertEqual(goodNode.body_1, goodData.get("body_1"))
        self.assertEqual(goodNode.body_2, goodData.get("body_2"))
        self.assertEqual(goodNode.lp_number, goodData.get("lp_number"))

        with self.assertRaises(ValidationError):
            badNode = LagrangeNode(**badData)