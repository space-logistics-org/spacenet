import unittest

from spacenet.schemas import (
    ClassOfSupply,
    ContinuousResource,
    DiscreteResource,
    Environment,
    ResourceType,
)


class TestResourceType(unittest.TestCase):
    def test_discrete_serialization(self):
        self.assertEqual(ResourceType.DISCRETE, "Discrete")

    def test_continuous_serialization(self):
        self.assertEqual(ResourceType.CONTINUOUS, "Continuous")


class TestDiscreteResource(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test resource",
            "class_of_supply": ClassOfSupply.COS_2,
            "environment": Environment.PRESSURIZED,
            "packing_factor": 0.5,
            "units": "kg",
            "description": "example description",
            "unit_mass": 1.0,
            "unit_volume": 0.1,
        }
        self.test_resource = DiscreteResource(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_resource.type, ResourceType.DISCRETE)
        self.assertEqual(self.test_resource.name, self.test_data.get("name"))
        self.assertEqual(
            self.test_resource.class_of_supply, self.test_data.get("class_of_supply")
        )
        self.assertEqual(
            self.test_resource.environment, self.test_data.get("environment")
        )
        self.assertEqual(
            self.test_resource.packing_factor, self.test_data.get("packing_factor")
        )
        self.assertEqual(self.test_resource.units, self.test_data.get("units"))
        self.assertEqual(
            self.test_resource.description, self.test_data.get("description")
        )
        self.assertEqual(self.test_resource.unit_mass, self.test_data.get("unit_mass"))
        self.assertEqual(
            self.test_resource.unit_volume, self.test_data.get("unit_volume")
        )


class TestContinuousResource(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "name": "test resource",
            "class_of_supply": ClassOfSupply.COS_2,
            "environment": Environment.PRESSURIZED,
            "packing_factor": 0.5,
            "units": "kg",
            "description": "example description",
            "unit_mass": 1.0,
            "unit_volume": 0.1,
        }
        self.test_resource = ContinuousResource(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_resource.type, ResourceType.CONTINUOUS)
        self.assertEqual(self.test_resource.name, self.test_data.get("name"))
        self.assertEqual(
            self.test_resource.class_of_supply, self.test_data.get("class_of_supply")
        )
        self.assertEqual(
            self.test_resource.environment, self.test_data.get("environment")
        )
        self.assertEqual(
            self.test_resource.packing_factor, self.test_data.get("packing_factor")
        )
        self.assertEqual(self.test_resource.units, self.test_data.get("units"))
        self.assertEqual(
            self.test_resource.description, self.test_data.get("description")
        )
        self.assertEqual(self.test_resource.unit_mass, self.test_data.get("unit_mass"))
        self.assertEqual(
            self.test_resource.unit_volume, self.test_data.get("unit_volume")
        )
