from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Union

from .. import database
# from ..auth import oauth2_scheme

from ..models import node as models
from ..schemas.node import *
from ..models.utilities import dictify_row


router = APIRouter()

Nodes = Union[
    SurfaceNode,
    OrbitalNode,
    LagrangeNode
]

CreateNodes = Union[
    SurfaceNodeCreate,
    OrbitalNodeCreate,
    LagrangeNodeCreate
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


@router.post("/", response_model=CreateNodes)
def create_node(
        node: Nodes,
        # token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    db_node = SCHEMA_TO_MODEL[type(node)](**node.dict())
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
    return db.query(models.Node).offset(skip).limit(limit).all()


@router.get("/{node_id}", response_model=ReadNodes)
def read_node(
        node_id: int,
        db: Session = Depends(database.get_db)
        ):
    db_node = db.query(models.Node).get(node_id)
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
    db_node = db.query(models.Node).get(node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node {:d} not found".format(node_id))
    for field in node.dict():
        if hasattr(db_node, field):
            setattr(db_node, field, node.dict()[field])
    db.commit()
    db.refresh(db_node)
    return db_node


@router.patch(
    "/{id_}",
    response_model=ReadNodes
)
def patch_node(
    id_: int, element: UpdateNodes, db: Session = Depends(database.get_db)
):
    db_node = db.query(models.node).get(id_)
    if db_node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No node found with id={id_}",
        )
    if node.type != db_node.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Node found with id={id_} is of type {db_node.type}; cannot update "
            f"type to {node.type} ",
        )
    for field_name, field in node.dict().items():
        if field_name != "type" and field is not None:
            setattr(db_node, field_name, field)
    db.commit()
    return db_node


@router.delete("/{node_id}", response_model=ReadNodes)
def delete_node(
        node_id: int,
        # token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    db_node = db.query(models.Node).get(node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node {:d} not found".format(node_id))
    as_dict = dictify_row(db_node)
    db.delete(db_node)
    db.commit()
    return as_dict
