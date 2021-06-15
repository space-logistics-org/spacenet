import unittest
from pydantic import ValidationError
from spacenet.schemas.resource import (
    DiscreteResource,
    ContinuousResource,
    ResourceType,
    ClassOfSupply,
)


class TestDisResource(unittest.TestCase):
    def test_good_data(self):
        name_ = "Fuel"
        type_ = ResourceType("discrete")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        res = DiscreteResource(
            name=name_,
            type=type_,
            cos=cos_,
            units=units_,
            unit_mass=unitmass_,
            unit_volume=unitvolume_,
        )
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.cos, cos_)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unit_mass, unitmass_)
        self.assertEqual(res.unit_volume, unitvolume_)

    def test_invalidType(self):
        name_ = "Fuel"
        type_ = 10
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidCOS(self):
        name_ = "Fuel"
        type_ = ResourceType("discrete")
        cos_ = "free"
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidMass(self):
        name_ = "Fuel"
        type_ = ResourceType("discrete")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidVolume(self):
        name_ = "Fuel"
        type_ = ResourceType("discrete")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )


class TestConResource(unittest.TestCase):
    def test_good_data(self):
        name_ = "Fuel"
        type_ = ResourceType("continuous")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        res = ContinuousResource(
            name=name_,
            type=type_,
            cos=cos_,
            units=units_,
            unit_mass=unitmass_,
            unit_volume=unitvolume_,
        )
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.cos, cos_)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unit_mass, unitmass_)
        self.assertEqual(res.unit_volume, unitvolume_)

    def test_invalidType(self):
        name_ = "Fuel"
        type_ = 10
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidCOS(self):
        name_ = "Fuel"
        type_ = ResourceType("continuous")
        cos_ = "free"
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidMass(self):
        name_ = "Fuel"
        type_ = ResourceType("continuous")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidVolume(self):
        name_ = "Fuel"
        type_ = ResourceType("continuous")
        cos_ = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                cos=cos_,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )
