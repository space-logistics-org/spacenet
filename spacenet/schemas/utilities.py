from typing import Dict, Optional, Type

from pydantic import BaseModel, create_model

__all__ = [
    "model_with_changed_field_types"
]


def model_with_changed_field_types(
        new_name: str, original: Type[BaseModel], base: Optional[Type[BaseModel]] = None,
        replaced_fields: Optional[Dict[str, Type]] = None
) -> Type[BaseModel]:
    if replaced_fields is None:
        return create_model(new_name, __config__=original.__config__, __base__=base)
    new_fields = {}
    for field, ty in original.__fields__.items():
        if field in replaced_fields:
            new_fields[field] = replaced_fields[field]
        else:
            new_fields[field] = ty
    return create_model(
        new_name, __config__=original.__config__, __base__=base, **new_fields
    )
