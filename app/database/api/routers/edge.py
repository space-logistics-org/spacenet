from typing import List

from fastapi import APIRouter, status

from .utilities import create_read_update_unions
from .base_funcs import list_all, read_item, create_item, update_item, delete_item
from ..models import edge as models
from ..schemas.constants import EDGE_SCHEMAS

# Build a new router
router = APIRouter()

Edges, ReadEdges, UpdateEdges = create_read_update_unions(EDGE_SCHEMAS)
NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


# Bind a route to list objects
router.get("/", response_model=List[ReadEdges])(list_all(models.Edge))


# Bind a route to read an object by ID
router.get("/{item_id}", response_model=ReadEdges, responses=NOT_FOUND_RESPONSE)(
    read_item(models.Edge, "edge")
)


# Bind a route to create a new object
router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadEdges)(
    create_item(create_schema=Edges)
)


# Bind a route to update an object by ID
router.patch("/{item_id}", response_model=ReadEdges, responses=NOT_FOUND_RESPONSE)(
    update_item(models.Edge, item_name="Edge", update_schema=UpdateEdges)
)


# Bind a route to delete an object by ID
router.delete("/{item_id}", response_model=ReadEdges)(
    delete_item(models.Edge, item_name="Edge")
)
