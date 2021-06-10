from typing import List, Union

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from ..schemas.element import *

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

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


@router.get(
    "/",
    response_model=List[ReadElements],
    description="List elements currently in the database.",
)
def list_elements(
    skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.get(
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Find a specific element in the database.",
)
def read_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.post(
    "/",
    response_model=ReadElements,
    status_code=status.HTTP_201_CREATED,
    description="Add a new element to the database.",
)
def create_element(element: Elements, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.patch(
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Update an existing element in the database.",
)
def patch_element(
    id_: int, element: UpdateElements, db: Session = Depends(database.get_db)
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.delete(
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Delete an element from the database.",
)
def delete_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")
