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

    def test_is_subclass_of(self):
        self.assertTrue(ClassOfSupply.COS_201.is_subclass_of(ClassOfSupply.COS_2))
        self.assertTrue(ClassOfSupply.COS_4011.is_subclass_of(ClassOfSupply.COS_4))
        self.assertTrue(ClassOfSupply.COS_4011.is_subclass_of(ClassOfSupply.COS_401))
        self.assertFalse(ClassOfSupply.COS_2.is_subclass_of(ClassOfSupply.COS_2))
        self.assertFalse(ClassOfSupply.COS_2.is_subclass_of(ClassOfSupply.COS_201))
        self.assertFalse(ClassOfSupply.COS_201.is_subclass_of(ClassOfSupply.COS_3))

    def test_cos_10_is_not_a_subclass_of_cos_1(self):
        self.assertFalse(ClassOfSupply.COS_10.is_subclass_of(ClassOfSupply.COS_1))
        self.assertFalse(ClassOfSupply.COS_101.is_subclass_of(ClassOfSupply.COS_10))
        self.assertTrue(ClassOfSupply.COS_101.is_subclass_of(ClassOfSupply.COS_1))

    def test_is_superclass_of(self):
        self.assertTrue(ClassOfSupply.COS_2.is_superclass_of(ClassOfSupply.COS_201))
        self.assertFalse(ClassOfSupply.COS_201.is_superclass_of(ClassOfSupply.COS_2))

    def test_is_instance_of(self):
        self.assertTrue(ClassOfSupply.COS_2.is_instance_of(ClassOfSupply.COS_2))
        self.assertTrue(ClassOfSupply.COS_201.is_instance_of(ClassOfSupply.COS_2))
        self.assertTrue(ClassOfSupply.COS_201.is_instance_of(2))
        self.assertFalse(ClassOfSupply.COS_2.is_instance_of(ClassOfSupply.COS_201))

    def test_get_base_class(self):
        self.assertEqual(ClassOfSupply.COS_9024.get_base_class(), ClassOfSupply.COS_9)
        self.assertEqual(ClassOfSupply.COS_10.get_base_class(), ClassOfSupply.COS_10)
        self.assertEqual(ClassOfSupply.COS_0.get_base_class(), ClassOfSupply.COS_0)
