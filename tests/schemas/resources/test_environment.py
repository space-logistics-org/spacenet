import unittest

from spacenet.schemas import Environment

class TestEnvironment(unittest.TestCase):
    def test_unpressirized_serialization(self):
        self.assertEqual(Environment.UNPRESSURIZED, "Unpressurized")
    
    def test_pressirized_serialization(self):
        self.assertEqual(Environment.PRESSURIZED, "Pressurized")
