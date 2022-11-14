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

    def test_add_element(self):
        element = Element(name="Test Element")
        self.test_location.add_element(element)
        self.assertIn(element, self.test_location.contents)

    def test_add_element_no_duplicate(self):
        element = Element(name="Test Element")
        self.test_location.add_element(element)
        self.test_location.add_element(element)
        self.assertIn(element, self.test_location.contents)
        self.assertEqual(len(self.test_location.contents), 1)

    def test_remove_element(self):
        element = Element(name="Test Element")
        self.test_location.add_element(element)
        self.test_location.remove_element(element)
        self.assertNotIn(element, self.test_location.contents)

    def test_remove_element_value_error(self):
        element = Element(name="Test Element")
        with self.assertRaises(ValueError):
            self.test_location.remove_element(element)
