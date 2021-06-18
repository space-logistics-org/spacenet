from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from ..models import node as models
from ..models.utilities import dictify_row
from ..schemas.node import *

# from ..auth import oauth2_scheme


router = APIRouter()

Nodes = Union[SurfaceNode, OrbitalNode, LagrangeNode]

UpdateNodes = Union[UpdateSurfaceNode, UpdateOrbitalNode, UpdateLagrangeNode]

ReadNodes = Union[ReadSurfaceNode, ReadOrbitalNode, ReadLagrangeNode]

SCHEMA_TO_MODEL = {
    SurfaceNode: models.SurfaceNode,
    OrbitalNode: models.OrbitalNode,
    LagrangeNode: models.LagrangeNode,
}

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ReadNodes)
def create_node(
    node: Nodes,
    # token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    db_node = SCHEMA_TO_MODEL[type(node)](**node.dict())
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node


@router.get("/", response_model=List[ReadNodes])
def list_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Node).offset(skip).limit(limit).all()


@router.get("/{node_id}", responses=NOT_FOUND_RESPONSE, response_model=ReadNodes)
def read_node(node_id: int, db: Session = Depends(database.get_db)):
    db_node = db.query(models.Node).get(node_id)
    if db_node is None:
        raise HTTPException(
            status_code=404, detail="Node {:d} not found".format(node_id)
        )
    return db_node


@router.patch(
    "/{node_id}",
    responses={**NOT_FOUND_RESPONSE, status.HTTP_409_CONFLICT: {"msg": str}},
    response_model=ReadNodes,
)
def update_node(
    node_id: int,
    node: UpdateNodes,
    # token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    db_node = db.query(models.Node).get(node_id)
    if db_node is None:
        raise HTTPException(
            status_code=404, detail="Node {:d} not found".format(node_id)
        )
    if node.type != db_node.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Node found with id={node_id} is of type {db_node.type}; cannot update "
            f"type to {node.type} ",
        )
    for field_name, field in node.dict().items():
        if field_name != "type" and field is not None:
            setattr(db_node, field_name, field)
    db.commit()
    db.refresh(db_node)
    return db_node


@router.delete("/{node_id}", responses=NOT_FOUND_RESPONSE, response_model=ReadNodes)
def delete_node(
    node_id: int,
    # token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    db_node = db.query(models.Node).get(node_id)
    if db_node is None:
        raise HTTPException(
            status_code=404, detail="Node {:d} not found".format(node_id)
        )
    as_dict = dictify_row(db_node)
    db.delete(db_node)
    db.commit()
    return as_dict
