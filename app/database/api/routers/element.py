from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from ..models import element as models
from ..schemas.element import *
from spacenet.schemas.element import ElementKind

router = APIRouter()

Elements = Union[
    Element,
    ElementCarrier,
    SurfaceVehicle,
    PropulsiveVehicle,
    RoboticAgent,
    HumanAgent,
    ResourceContainer,
]

UpdateElements = Union[
    UpdateElement,
    UpdateElementCarrier,
    UpdateSurfaceVehicle,
    UpdatePropulsiveVehicle,
    UpdateRoboticAgent,
    UpdateHumanAgent,
    UpdateResourceContainer,
]

ReadElements = Union[
    ReadElement,
    ReadElementCarrier,
    ReadSurfaceVehicle,
    ReadPropulsiveVehicle,
    ReadRoboticAgent,
    ReadHumanAgent,
    ReadResourceContainer,
]

SCHEMA_TO_MODEL = {
    Element: models.Element,
    ElementCarrier: models.ElementCarrier,
    ResourceContainer: models.ResourceContainer,
    HumanAgent: models.HumanAgent,
    RoboticAgent: models.RoboticAgent,
    PropulsiveVehicle: models.PropulsiveVehicle,
    SurfaceVehicle: models.SurfaceVehicle,
}

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}

KIND_TO_SCHEMA = {
    ElementKind.Element: Element,
    ElementKind.ElementCarrier: ElementCarrier,
    ElementKind.ResourceContainer: ResourceContainer,
    ElementKind.HumanAgent: HumanAgent,
    ElementKind.RoboticAgent: RoboticAgent,
    ElementKind.Surface: SurfaceVehicle,
    ElementKind.Propulsive: PropulsiveVehicle
}


@router.get(
    "/",
    response_model=List[ReadElements],
    description="List elements currently in the database.",
)
def list_elements(db: Session = Depends(database.get_db)):
    db_elements = db.query(models.Element).all()
    return db_elements


@router.get(
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Find a specific element in the database.",
)
def read_element(id_: int, db: Session = Depends(database.get_db)):
    db_element = db.query(models.Element).get(id_)
    if db_element is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No element found with id={id_}",
        )
    return db_element


@router.post(
    "/",
    response_model=ReadElements,
    status_code=status.HTTP_201_CREATED,
    description="Add a new element to the database.",
)
def create_element(element: Elements, db: Session = Depends(database.get_db)):
    db_element = SCHEMA_TO_MODEL[type(element)](**element.dict())
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element


@router.patch(
    "/{id_}",
    response_model=ReadElements,
    responses={**NOT_FOUND_RESPONSE, status.HTTP_409_CONFLICT: {"msg": str}},
    description="Update an existing element in the database.",
)
def patch_element(
    id_: int, element: UpdateElements, db: Session = Depends(database.get_db)
):
    db_element = db.query(models.Element).get(id_)
    if db_element is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No element found with id={id_}",
        )
    if element.type != db_element.type:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Element found with id={id_} is of type {db_element.type}; cannot update "
            f"type to {element.type} ",
        )
    for field_name, field in element.dict().items():
        if field_name != "type" and field is not None:
            setattr(db_element, field_name, field)
    db.commit()
    return db_element


@router.delete(
    "/{id_}",
    responses=NOT_FOUND_RESPONSE,
    description="Delete an element from the database.",
)
def delete_element(id_: int, db: Session = Depends(database.get_db)):
    db_element = db.query(models.Element).get(id_)
    if db_element is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No element found with id={id_}",
        )
    db.delete(db_element)
    db.commit()
    return {"msg": f"Successfully deleted element with id={id_}"}


# TODO: test all of these after implementing patch
