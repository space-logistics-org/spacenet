from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from ..models import resource as models
from ..models.utilities import dictify_row
from ..schemas.resource import *
from spacenet.schemas.resource import ResourceType

router = APIRouter()

Resources = Union[ContinuousResource, DiscreteResource]

UpdateResources = Union[ContinuousUpdate, DiscreteUpdate]

ReadResources = Union[ContinuousRead, DiscreteRead]

SCHEMA_TO_MODEL = {
    ContinuousResource: models.ContinuousResource,
    DiscreteResource: models.DiscreteResource,
}

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


def to_db_kwargs(resource: Resources) -> Dict[str, Any]:
    excluded = {"unit_mass", "unit_volume"}
    ret = {k: v for k, v in resource.dict().items() if k not in excluded}
    suffix = "_i" if isinstance(resource, DiscreteResource) else "_f"
    ret["unit_mass" + suffix] = resource.unit_mass
    ret["unit_volume" + suffix] = resource.unit_volume
    return ret


def to_schema_kwargs(
    db_model: Union[models.DiscreteResource, models.ContinuousResource]
) -> Dict[str, Any]:
    suffix = "_i" if isinstance(db_model, models.DiscreteResource) else "_f"
    return {
        "id": db_model.id,
        "type": db_model.type,
        "name": db_model.name,
        "description": db_model.description,
        "class_of_supply": db_model.class_of_supply,
        "units": db_model.units,
        "unit_mass": getattr(db_model, "unit_mass" + suffix),
        "unit_volume": getattr(db_model, "unit_volume" + suffix),
    }


@router.get(
    "/",
    response_model=List[ReadResources],
    description="List resources currently in the database.",
)
def list_resources(db: Session = Depends(database.get_db)):
    db_resources = db.query(models.Resource).all()
    return [to_schema_kwargs(resource) for resource in db_resources]


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
    return to_schema_kwargs(db_resource)


@router.post(
    "/",
    response_model=ReadResources,
    status_code=status.HTTP_201_CREATED,
    description="Add a new resource to the database.",
)
def create_resource(resource: Resources, db: Session = Depends(database.get_db)):
    db_resource = SCHEMA_TO_MODEL[type(resource)](**to_db_kwargs(resource))
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return to_schema_kwargs(db_resource)


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
            f"update type to {resource.type} ",
        )
    suffix = "_i" if resource.type == ResourceType.discrete else "_f"
    for field_name, field in resource.dict().items():
        if field_name != "type" and field is not None:
            if field_name == "unit_mass" or field_name == "unit_volume":
                field_name += suffix
            setattr(db_resource, field_name, field)
    db.commit()
    return to_schema_kwargs(db_resource)


@router.delete(
    "/{id_}",
    response_model=ReadResources,
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
    suffix = "_i" if db_resource.type == ResourceType.discrete else "_f"
    as_dict = dictify_row(db_resource)
    db.delete(db_resource)
    db.commit()
    for field in ("unit_mass", "unit_volume"):
        as_dict[field] = as_dict[field + suffix]
        del as_dict[field + suffix]
    return as_dict
