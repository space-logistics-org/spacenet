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

from spacenet.schemas.mixins import OptionalFields, RequiresID


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

    def test_all_made_optional(self):
        class OptionalModel(self.Model, OptionalFields):
            pass

        for field_name, field in self.Model.__fields__.items():
            exp_field = copy.deepcopy(field)
            exp_field.required = False
            exp_field.default = None
            actual_field = OptionalModel.__fields__[field_name]
            # using repr b/c __eq__ isn't implemented for Field
            self.assertEqual(repr(exp_field), repr(actual_field))

    def test_some_made_optional(self):
        class PartialOptionalModel(self.Model, OptionalFields, excluded_fields={"a"}):
            pass

        optional_fields = (
            field_name
            for field_name in set(self.Model.__fields__.keys()).difference({"a"})
        )
        for field_name in optional_fields:
            field = self.Model.__fields__[field_name]
            exp_field = copy.deepcopy(field)
            exp_field.required = False
            exp_field.default = None
            actual_field = PartialOptionalModel.__fields__[field_name]
            self.assertEqual(repr(exp_field), repr(actual_field))
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

    def test_requires_uuid(self):
        class ModelWithID(self.Model, RequiresID):
            pass

        self.assertEqual(len(ModelWithID.__fields__), 1)
        field_name, field = ModelWithID.__fields__.popitem()
        self.assertEqual(field_name, "id_")
        self.assertIsInstance(field, ModelField)
        self.assertEqual(UUID, field.type_)
        self.assertTrue(field.required)
