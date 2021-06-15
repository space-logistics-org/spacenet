from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from .. import database
# from ..auth import oauth2_scheme

from ..models import node as models
from ..schemas.node import *


router = APIRouter()

Nodes = Union[
    SurfaceNode,
    OrbitalNode,
    LagrangeNode
]

UpdateNodes = Union[
    UpdateSurfaceNode,
    UpdateOrbitalNode,
    UpdateLagrangeNode
]

ReadNodes = Union[
    ReadSurfaceNode,
    ReadOrbitalNode,
    ReadLagrangeNode
]

SCHEMA_TO_MODEL = {
    SurfaceNode: models.SurfaceNode,
    OrbitalNode: models.OrbitalNode,
    LagrangeNode: models.LagrangeNode
}

TYPE_TO_SCHEMA = {
    NodeType.SurfaceNode: SurfaceNode,
    NodeType.OrbitalNode: OrbitalNode,
    NodeType.LagrangeNode: LagrangeNode
}


@router.post("/", response_model=ReadNodes)
def create_node(
        node: Nodes,
        # token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    db_node = models.node(**node.dict())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


@router.get("/", response_model=List[ReadNodes])
def list_nodes(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(database.get_db)
        ):
    return db.query(models.node).offset(skip).limit(limit).all()


@router.get("/{node_id}", response_model=ReadNodes)
def read_node(
        node_id: int,
        db: Session = Depends(database.get_db)
        ):
    db_node = db.query(models.node).get(node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node {:d} not found".format(node_id))
    return db_node


@router.put("/{node_id}", response_model=ReadNodes)
def update_node(
        node_id: int,
        node: Nodes,
        # token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    db_node = db.query(models.node).get(node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node {:d} not found".format(node_id))
    for field in node.dict():
        if hasattr(db_node, field):
            setattr(db_node, field, node.dict()[field])
    db.commit()
    db.refresh(db_node)
    return db_node


@router.delete("/{node_id}", response_model=ReadNodes)
def delete_node(
        node_id: int,
        # token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    db_node = db.query(models.node).get(node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node {:d} not found".format(node_id))
    db.delete(db_node)
    db.commit()
    return db_node
