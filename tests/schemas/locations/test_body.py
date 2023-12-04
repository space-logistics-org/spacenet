import unittest

from spacenet.schemas import Body


class TestBody(unittest.TestCase):
    def test_sun_serialization(self):
        self.assertEqual(Body.SUN, "Sun")

    def test_earth_serialization(self):
        self.assertEqual(Body.EARTH, "Earth")

    def test_moon_serialization(self):
        self.assertEqual(Body.MOON, "Moon")

    def test_mars_serialization(self):
        self.assertEqual(Body.MARS, "Mars")
