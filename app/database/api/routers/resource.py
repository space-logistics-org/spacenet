"""
This module specifies a CRUD route for the resource schema.
"""

from .base_router import CRUDRouter
from ..models import resource as models
from ..schemas.constants import RESOURCE_SCHEMAS

router = CRUDRouter(
    table=models.Resource,
    name="resource",
    schemas=RESOURCE_SCHEMAS,
)
