from typing import List, Union
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from .. import database
from ..models import edge as models
from ..schemas.edge_routing import *
from ..models.utilities import dictify_row

# Build a new router
router = APIRouter()

Edges = Union[SurfaceEdge, SpaceEdge, FlightEdge]
UpdateEdges = Union[UpdateSurfaceEdge, UpdateSpaceEdge, UpdateFlightEdge]
ReadEdges = Union[ReadSurfaceEdge, ReadSpaceEdge, ReadFlightEdge]

SCHEMA_TO_MODEL = {
    SurfaceEdge: models.SurfaceEdge,
    SpaceEdge: models.SpaceEdge,
    FlightEdge: models.FlightEdge,
}


# Bind a route to list objects
@router.get("/", response_model=List[ReadEdges])
def list_edges(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    db_edges = db.query(models.Edge).offset(skip).limit(limit).all()
    return db_edges


# Bind a route to read an object by ID
@router.get("/{edge_id}", response_model=ReadEdges)
def read_edge(edge_id: int, db: Session = Depends(database.get_db)):
    db_edge = db.query(models.Edge).get(edge_id)
    if db_edge is None:
        raise HTTPException(
            status_code=404, detail="Edge {:d} not found".format(edge_id)
        )
    return db_edge


# Bind a route to create a new object
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadEdges)
def create_edge(edge: Edges, db: Session = Depends(database.get_db)):
    db_edge = SCHEMA_TO_MODEL[type(edge)](**edge.dict())
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    print("created edge", dictify_row(db_edge))
    return db_edge


# Bind a route to update an object by ID
@router.put("/{edge_id}", response_model=ReadEdges)
def update_edge(
    edge_id: int, edge: UpdateEdges, db: Session = Depends(database.get_db)
):
    db_edge = db.query(models.Edge).get(edge_id)
    if db_edge is None:
        raise HTTPException(
            status_code=404, detail="Edge {:d} not found".format(edge_id)
        )
    if edge.type != db_edge.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Edge found with id={edge_id} is of type {db_edge.type}; cannot update "
                   f"type to {edge.type} ",
        )
    for field in edge.dict():
        if hasattr(db_edge, field):
            setattr(db_edge, field, edge.dict()[field])
    db.commit()
    return db_edge


# Bind a route to delete an object by ID
@router.delete("/{edge_id}", response_model=ReadEdges)
def delete_edge(edge_id: int, db: Session = Depends(database.get_db)):
    db_edge = db.query(models.Edge).get(edge_id)
    if db_edge is None:
        raise HTTPException(
            status_code=404, detail="Edge {:d} not found".format(edge_id)
        )
    as_dict = dictify_row(db_edge)
    db.delete(db_edge)
    db.commit()
    return as_dict
