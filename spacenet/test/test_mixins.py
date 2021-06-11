"""
This module contains tests for mixins defined, and checks that the behavior of the mixins which
compose more specific mixins (such as RequiresOnlyType) is correct. Uses simple equivalence
partitions.
"""
import copy
import unittest
from uuid import UUID

from pydantic import BaseModel, Field, conint
from pydantic.fields import ModelField

from spacenet.schemas.mixins import OptionalFields, RequiresUUID


class TestOptionalFields(unittest.TestCase):
    """
    Tests for the OptionalFields class.
    Partition on number of excluded fields:
        0
        > 0
    """

    class Model(BaseModel):
        a: int
        b: float = Field(description="test")
        c: conint(ge=0)

    def testAllMadeOptional(self):
        class OptionalModel(self.Model, OptionalFields):
            pass

        for fieldName, field in self.Model.__fields__.items():
            expField = copy.deepcopy(field)
            expField.required = False
            expField.default = None
            actualField = OptionalModel.__fields__[fieldName]
            # using repr b/c __eq__ isn't implemented for Field
            self.assertEqual(repr(expField), repr(actualField))

    def testSomeMadeOptional(self):
        class PartialOptionalModel(self.Model, OptionalFields, excluded_fields={"a"}):
            pass

        optional_fields = (
            fieldName
            for fieldName in set(self.Model.__fields__.keys()).difference({"a"})
        )
        for fieldName in optional_fields:
            field = self.Model.__fields__[fieldName]
            expField = copy.deepcopy(field)
            expField.required = False
            expField.default = None
            actualField = PartialOptionalModel.__fields__[fieldName]
            self.assertEqual(repr(expField), repr(actualField))
        self.assertEqual(
            repr(TestOptionalFields.Model.__fields__["a"]),
            repr(PartialOptionalModel.__fields__["a"]),
        )


class TestRequiresUUID(unittest.TestCase):
    """
    Tests for the RequiresUUID class.
    """

    class Model(BaseModel):
        pass

    def testRequiresUUID(self):
        class ModelWithUUID(self.Model, RequiresUUID):
            pass

        self.assertEqual(len(ModelWithUUID.__fields__), 1)
        fieldName, field = ModelWithUUID.__fields__.popitem()
        self.assertEqual(fieldName, "id_")
        self.assertIsInstance(field, ModelField)
        self.assertEqual(UUID, field.type_)
        self.assertTrue(field.required)
