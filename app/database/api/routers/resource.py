from .base_router import CRUDRouter
from ..models import resource as models
from ..schemas.constants import RESOURCE_SCHEMAS

router = CRUDRouter(
    table=models.Resource,
    name_lower="resource",
    name_capitalized="Resource",
    schemas=RESOURCE_SCHEMAS,
)
