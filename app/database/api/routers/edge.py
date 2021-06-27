from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .utilities import create_read_update_unions
from .base_funcs import list_all, read_item, create_item, update_item, delete_item
from .. import database
from ..models import edge as models
from ..models.utilities import SCHEMA_TO_MODEL, dictify_row
from ..schemas.constants import EDGE_SCHEMAS

# Build a new router
router = APIRouter()

Edges, ReadEdges, UpdateEdges = create_read_update_unions(EDGE_SCHEMAS)
NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


# Bind a route to list objects
@router.get("/", response_model=List[ReadEdges])
def list_edges(db: Session = Depends(database.get_db)):
    return list_all(
        table=models.Edge,
        db=db
    )


# Bind a route to read an object by ID
@router.get("/{edge_id}", response_model=ReadEdges, responses=NOT_FOUND_RESPONSE)
def read_edge(edge_id: int, db: Session = Depends(database.get_db)):
    return read_item(
        table=models.Edge,
        item_name="Edge",
        item_id=edge_id,
        db=db
    )


# Bind a route to create a new object
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadEdges)
def create_edge(edge: Edges, db: Session = Depends(database.get_db)):
    return create_item(
        item=edge,
        db=db,
    )


# Bind a route to update an object by ID
@router.patch("/{edge_id}", response_model=ReadEdges, responses=NOT_FOUND_RESPONSE)
def update_edge(
        edge_id: int, edge: UpdateEdges, db: Session = Depends(database.get_db)
):
    return update_item(
        table=models.Edge,
        item_name="Edge",
        item_id=edge_id,
        item=edge,
        db=db
    )


# Bind a route to delete an object by ID
@router.delete("/{edge_id}", response_model=ReadEdges)
def delete_edge(edge_id: int, db: Session = Depends(database.get_db)):
    return delete_item(
        table=models.Edge,
        item_name="Edge",
        item_id=edge_id,
        db=db
    )
