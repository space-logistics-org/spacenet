"""
This module specifies a CRUD route for the element schema.
"""

from .base_router import CRUDRouter
from ..models import element as models
from ..schemas.constants import ELEMENT_SCHEMAS

router = CRUDRouter(
    table=models.Element,
    name_lower="element",
    name_capitalized="Element",
    schemas=ELEMENT_SCHEMAS,
)
