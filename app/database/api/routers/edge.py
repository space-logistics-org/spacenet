from .base_router import CRUDRouter
from .utilities import create_read_update_unions
from ..models import edge as models
from ..schemas.constants import EDGE_SCHEMAS

Edges, ReadEdges, UpdateEdges = create_read_update_unions(EDGE_SCHEMAS)
router = CRUDRouter(
    table=models.Edge,
    name_lower="edge",
    name_capitalized="Edge",
    create_schema=Edges,
    read_schema=ReadEdges,
    update_schema=UpdateEdges,
)
