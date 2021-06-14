from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from ..models import resource as models
from ..schemas.resource import *
from spacenet.schemas.resource import ResourceType

router = APIRouter()

Resources = Union[ContinuousResource, DiscreteResource]

UpdateResources = Union[UpdateContinuous, UpdateDiscrete]

ReadResources = Union[ReadContinuous, ReadDiscrete]

SCHEMA_TO_MODEL = {
    ResourceType.continuous: ContinuousResource,
    ResourceType.discrete: DiscreteResource,
}

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


@router.get(
    "/",
    response_model=List[ReadResources],
    description="List resources currently in the database.",
)
def list_resources(db: Session = Depends(database.get_db)):
    db_resources = db.query(models.Resource).all()
    return db_resources


@router.get(
    "/{id_}",
    response_model=ReadResources,
    description="Find a specific resource in the database.",
)
def read_resource(id_: int, db: Session = Depends(database.get_db)):
    db_resource = db.query(models.Resource).get(id_)
    if db_resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No resource found with id={id_}",
        )
    return db_resource


@router.post(
    "/",
    response_model=ReadResources,
    status_code=status.HTTP_201_CREATED,
    description="Add a new resource to the database.",
)
def create_resource(resource: Resources, db: Session = Depends(database.get_db)):
    db_resource = SCHEMA_TO_MODEL[type(resource)](**resource.dict())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.patch(
    "/{id_}",
    response_model=ReadResources,
    responses={**NOT_FOUND_RESPONSE, status.HTTP_409_CONFLICT: {"msg": str}},
    description="Update an existing resource in the database.",
)
def patch_resource(
    id_: int, resource: UpdateResources, db: Session = Depends(database.get_db)
):
    db_resource = db.query(models.Resource).get(id_)
    if db_resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No resource found with id={id_}",
        )
    if resource.type != db_resource.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resource found with id={id_} is of type {db_resource.type}; cannot "
            f"update "
            f"type to {resource.type} ",
        )
    for field_name, field in resource.dict().items():
        if field_name != "type" and field is not None:
            setattr(db_resource, field_name, field)
    db.commit()
    return db_resource


@router.delete(
    "/{id_}",
    responses=NOT_FOUND_RESPONSE,
    description="Delete a resource from the database.",
)
def delete_resource(id_: int, db: Session = Depends(database.get_db)):
    db_resource = db.query(models.Resource).get(id_)
    if db_resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No resource found with id={id_}",
        )
    db.delete(db_resource)
    db.commit()
    return {"msg": f"Successfully deleted resource with id={id_}"}
