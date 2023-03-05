import unittest

from spacenet.schemas import ClassOfSupply

class TestClassOfSupply(unittest.TestCase):
    def test_cos_0_serialization(self):
        self.assertEqual(ClassOfSupply.COS_0, 0)

    def test_cos_1_serialization(self):
        self.assertEqual(ClassOfSupply.COS_1, 1)
        
    def test_cos_0_get_name(self):
        self.assertEqual(ClassOfSupply.COS_0.get_name(), "None")
        
    def test_cos_1_get_name(self):
        self.assertEqual(ClassOfSupply.COS_1.get_name(), "Propellants and Fuels")