"""
This module contains tests for mixins defined, and checks that the behavior of the mixins which
compose more specific mixins (such as RequiresOnlyType) is correct. Uses simple equivalence
partitions.
"""
import copy

import pytest
from pydantic import BaseModel, Field, conint
from pydantic.fields import ModelField

from ...src.schemas.mixins import OptionalFields, RequiresID

pytestmark = [pytest.mark.unit, pytest.mark.schema]


class TestOptionalFields:
    """
    Tests for the OptionalFields class.
    Partition on number of excluded fields:
        0
        > 0
    """

    # noinspection PyMissingOrEmptyDocstring
    class Model(BaseModel):
        a: int
        b: float = Field(description="test")
        c: conint(ge=0)

    def test_all_made_optional(self):
        # noinspection PyMissingOrEmptyDocstring
        class OptionalModel(self.Model, OptionalFields):
            pass

        for field_name, field in self.Model.__fields__.items():
            exp_field = copy.deepcopy(field)
            exp_field.required = False
            exp_field.default = None
            exp_field.allow_none = True
            actual_field = OptionalModel.__fields__[field_name]
            # using repr b/c __eq__ isn't implemented for Field
            assert repr(exp_field) == repr(actual_field)

    def test_some_made_optional(self):
        # noinspection PyMissingOrEmptyDocstring
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
            exp_field.allow_none = True
            actual_field = PartialOptionalModel.__fields__[field_name]
            assert repr(exp_field) == repr(actual_field)
        assert repr(self.Model.__fields__["a"]) == repr(
            PartialOptionalModel.__fields__["a"]
        )


class TestRequiresID:
    """
    Tests for the RequiresID class.
    """

    # noinspection PyMissingOrEmptyDocstring
    class Model(BaseModel):
        pass

    def test_requires_uuid(self):
        # noinspection PyMissingOrEmptyDocstring
        class ModelWithID(self.Model, RequiresID):
            pass

        assert len(ModelWithID.__fields__) == 1
        field_name, field = ModelWithID.__fields__.popitem()
        assert field_name == "id"
        assert isinstance(field, ModelField)
        assert int == field.type_
        assert field.required
