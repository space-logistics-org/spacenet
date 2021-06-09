import unittest
from pydantic import ValidationError
from spacenet.schemas.Resource import DiscreteResource, ContinuousResource

class TestDisResource(unittest.TestCase):
    def test_good_data(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        res = DiscreteResource(id = id_, name = name_, type = type_, cos = cos_, units = units_, unitmass = unitmass_, unitvolume = unitvolume_)
        self.assertEqual(res.id, id_)
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.cos, cos_)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unitmass, unitmass_)
        self.assertEqual(res.unitvolume, unitvolume_)
    def test_invalidID(self):
        id_ = "G"
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidName(self):
        id_ = 1
        name_ = 100
        type_ = "discrete"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidType(self):
        id_ = 1
        name_ = "Fuel"
        type_ = 10
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidCOS(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = "free"
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidUnits(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = 101
        units_ = 5
        unitmass_ = 105
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidMass(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = 101
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidVolume(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "discrete"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)

class TestConResource(unittest.TestCase):
    def test_good_data(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
        self.assertEqual(res.id, id_)
        self.assertEqual(res.name, name_)
        self.assertEqual(res.type, type_)
        self.assertEqual(res.cos, cos_)
        self.assertEqual(res.units, units_)
        self.assertEqual(res.unitmass, unitmass_)
        self.assertEqual(res.unitvolume, unitvolume_)
    def test_invalidID(self):
        id_ = "G"
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidName(self):
        id_ = 1
        name_ = 100
        type_ = "continuous"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidType(self):
        id_ = 1
        name_ = "Fuel"
        type_ = 10
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidCOS(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = "free"
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidUnits(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = 101
        units_ = 5
        unitmass_ = 105.5
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidMass(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = 101
        units_ = "kg"
        unitmass_ = -10
        unitvolume_ = 150.8
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)
    def test_invalidVolume(self):
        id_ = 1
        name_ = "Fuel"
        type_ = "continuous"
        cos_ = 101
        units_ = "kg"
        unitmass_ = 105.5
        unitvolume_ = "vol"
        with self.assertRaises(ValidationError):
            res = DiscreteResource(id=id_, name=name_, type=type_, cos=cos_, units=units_, unitmass=unitmass_, unitvolume=unitvolume_)