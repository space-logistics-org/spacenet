import unittest

from spacenet.schemas import Location, Element

class TestLocation(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "location"
        }
        self.test_location = Location(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_location.name, self.test_data.get("name"))
