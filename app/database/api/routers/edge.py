from .base_router import CRUDRouter
from ..models import edge as models
from ..schemas.constants import EDGE_SCHEMAS

router = CRUDRouter(
    table=models.Edge, name_lower="edge", name_capitalized="Edge", schemas=EDGE_SCHEMAS,
)
