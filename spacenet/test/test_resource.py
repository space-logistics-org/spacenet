import json
import unittest

import pkg_resources
import pytest
from pydantic import ValidationError

import spacenet
from spacenet.schemas.resource import (
    DiscreteResource,
    ContinuousResource,
    ResourceType,
    ClassOfSupply,
)
from .lunar_sortie_utils import resources

pytestmark = [pytest.mark.unit, pytest.mark.resource, pytest.mark.schema]


class TestDisResource(unittest.TestCase):
    def test_good_data(self):
        name_ = "Fuel"
        type_ = ResourceType("Discrete")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        res = DiscreteResource(
            name=name_,
            type=type_,
            class_of_supply=cos,
            units=units_,
            unit_mass=unitmass_,
            unit_volume=unitvolume_,
        )
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.class_of_supply, cos)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unit_mass, unitmass_)
        self.assertEqual(res.unit_volume, unitvolume_)

    def test_invalidType(self):
        name_ = "Fuel"
        type_ = 10
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidCOS(self):
        name_ = "Fuel"
        type_ = ResourceType("Discrete")
        cos = "free"
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidMass(self):
        name_ = "Fuel"
        type_ = ResourceType("Discrete")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidVolume(self):
        name_ = "Fuel"
        type_ = ResourceType("Discrete")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = DiscreteResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )


class TestConResource(unittest.TestCase):

    def test_good_data(self):
        name_ = "Fuel"
        type_ = ResourceType("Continuous")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        res = ContinuousResource(
            name=name_,
            type=type_,
            class_of_supply=cos,
            units=units_,
            unit_mass=unitmass_,
            unit_volume=unitvolume_,
        )
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.class_of_supply, cos)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unit_mass, unitmass_)
        self.assertEqual(res.unit_volume, unitvolume_)

    def test_invalidType(self):
        name_ = "Fuel"
        type_ = 10
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidCOS(self):
        name_ = "Fuel"
        type_ = ResourceType("Continuous")
        cos = "free"
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidMass(self):
        name_ = "Fuel"
        type_ = ResourceType("Continuous")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )

    def test_invalidVolume(self):
        name_ = "Fuel"
        type_ = ResourceType("Continuous")
        cos = ClassOfSupply(101)
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = ContinuousResource(
                name=name_,
                type=type_,
                class_of_supply=cos,
                units=units_,
                unit_mass=unitmass_,
                unit_volume=unitvolume_,
            )


KIND_TO_SCHEMA = {
    ResourceType.continuous: ContinuousResource,
    ResourceType.discrete: DiscreteResource
}


@pytest.mark.lunar_sortie
def test_lunar_sortie_resources(resources):
    for resource_obj in resources:
        constructor = KIND_TO_SCHEMA[resource_obj["type"]]
        resource = constructor.parse_obj(resource_obj)
        for attr, value in resource_obj.items():
            assert value == getattr(resource, attr)
