from typing import List, Union
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session

from .. import database
from ..models import edge as models
from ..schemas.edge import *

#Build a new router
router = APIRouter()

Edges = Union[SurfaceEdge, SpaceEdge, FlightEdge]
SCHEMA_TO_MODEL = {SurfaceEdge: models.SurfaceEdge, SpaceEdge: models.SpaceEdge, FlightEdge: models.FlightEdge}

#Bind a route to list objects
@router.get("/", response_model = List[Edges])
def list_edges(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):

    db_edges = db.query(models.Edge).offset(skip).limit(limit).all()
    
    return db_edges

#Bind a route to read an object by ID
@router.get("/{edge_id}", response_model = Edges)
def read_edge(edge_id: int, db: Session = Depends(database.get_db)):
    
    db_edge = db.query(models.Edge).get(edge_id)
    
    if db_edge is None:
        raise HTTPException(status_code = 404, detail = "Edge {:d} not found".format(edge_id))
    
    return db_edge

#Bind a route to create a new object
@router.post("/", response_model = Edges)
def create_edge(edge: Edges, db: Session = Depends(database.get_db)): 

    db_edge = models.Edge(**edge.dict())

    db.add(db_edge)

    db.commit()

    db.refresh(db_edge)

    return db_edge

#Bind a route to update an object by ID
@router.put("/{edge_id}", response_model = Edges)
def update_edge(edge_id: int, edge: Edges, db: Session = Depends(database.get_db)):

    db_edge = db.query(models.Edge).get(edge_id)

    if db_edge is None:
        raise HTTPException(status_code = 404, detail = "Edge {:d} not found".format(edge_id))

    for field in edge.dict():
        if hasattr(db_edge, field):
            setattr(db_edge, field, edge.dict()[field])

    db.commit()
    db.refresh(db_edge)

    return db_edge

#Bind a route to delete an object by ID
@router.delete("/{edge_id}", response_model = Edges)
def delete_edge(edge_id: int, db: Session = Depends(database.get_db)):

    db_edge = db.query(models.Edge).get(edge_id)

    if db_edge is None:
        raise HTTPException(status_code = 404, detail = "Edge {:d} not found".format(edge_id))

    db.delete(db_edge)
    db.commit()

    return db_edge