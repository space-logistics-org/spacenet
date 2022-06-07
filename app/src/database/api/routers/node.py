"""
This module specifies a CRUD route for the node schema.
"""

from .base_router import CRUDRouter
from ..models import node as models
from ..schemas.constants import NODE_SCHEMAS

router = CRUDRouter(
    table=models.Node,
    name="node",
    schemas=NODE_SCHEMAS,
)
