from .base_router import CRUDRouter
from ..models import state as models
from ..schemas.constants import STATE_SCHEMAS

router = CRUDRouter(
    table=models.State,
    name_lower="state",
    name_capitalized="State",
    schemas=STATE_SCHEMAS
)
