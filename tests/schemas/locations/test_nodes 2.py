import unittest

from spacenet.schemas import Body, LagrangeNode, OrbitalNode, SurfaceNode


class TestSurfaceNode(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test node",
            "latitude": 40.74259,
            "longitude": -74.02686
        }
        self.test_node = SurfaceNode(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_node.name, self.test_data.get("name"))
        self.assertEqual(self.test_node.latitude, self.test_data.get("latitude"))
        self.assertEqual(self.test_node.longitude, self.test_data.get("longitude"))

class TestOrbitalNode(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test node",
            "apoapsis": 400e3,
            "periapsis": 401e3,
            "inclination": 52.5
        }
        self.test_node = OrbitalNode(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_node.name, self.test_data.get("name"))
        self.assertEqual(self.test_node.apoapsis, self.test_data.get("apoapsis"))
        self.assertEqual(self.test_node.periapsis, self.test_data.get("periapsis"))
        self.assertEqual(self.test_node.inclination, self.test_data.get("inclination"))

class TestLagrangeNode(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test node",
            "body_2": Body.MOON,
            "lp_number": 1
        }
        self.test_node = LagrangeNode(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_node.name, self.test_data.get("name"))
        self.assertEqual(self.test_node.body_2, self.test_data.get("body_2"))
        self.assertEqual(self.test_node.lp_number, self.test_data.get("lp_number"))


