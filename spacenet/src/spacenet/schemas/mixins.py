"""
This module contains general-purpose mixins for generating common single behaviors which might
be useful across different schema modules.
"""
from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field
from fastapi_camelcase import CamelModel

__all__ = [
    "RequiresID",
    "RequiresOnlyType",
    "OptionalFields",
    "ReadSchema",
    "ImmutableBaseModel",
]


class RequiresID(BaseModel, ABC):
    """
    A mixin which requires each instantiation of a schema contain an integral ID field.
    """

    id: int = Field(title="ID")


class OptionalFields(BaseModel, ABC):
    """
    A mixin which makes a subset of the fields of its subclasses optional.
    """

    def __init_subclass__(cls, **kwargs):
        excluded_fields = kwargs.pop("excluded_fields", set())
        assert excluded_fields.issubset(cls.__fields__), (
            f"required_fields must be a subset " f"of the existing fields"
        )
        super().__init_subclass__()
        optional_fields = (
            field
            for fieldName, field in cls.__fields__.items()
            if fieldName not in excluded_fields
        )
        for field in optional_fields:
            field.default = None
            field.outer_type_ = Optional
            field.required = False
            field.allow_none = True


class RequiresOnlyType(OptionalFields):
    """
    A mixin which requires only the "type" field, but should only be applied to models
    with a "type" field.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(excluded_fields={"type"}, **kwargs)


class ReadSchema(RequiresID):
    """
    A mixin which requires an ID field as in RequiresID but also allows construction from
    arbitrary class instances via the ``from_orm`` method.
    """

    class Config:
        """
        Configuration inner class allowing construction from arbitrary class instances
        """

        orm_mode = True


class ImmutableBaseModel(CamelModel):
    """
    A mixin which forbids mutation of the schema after instantiation.
    """

    class Config:
        """
        Configuration inner class forbidding mutation of the schema after instantiation.
        """

        allow_mutation = False
        frozen = True

    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))
