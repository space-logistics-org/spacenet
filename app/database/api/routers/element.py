from typing import List, Union

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
<<<<<<< HEAD
from spacenet.schemas import element as schemas
=======
from ..schemas.element import *
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296

router = APIRouter()

Elements = Union[
<<<<<<< HEAD
    schemas.Element,
    schemas.ElementCarrier,
    schemas.SurfaceVehicle,
    schemas.PropulsiveVehicle,
    schemas.RoboticAgent,
    schemas.HumanAgent,
    schemas.ResourceContainer,
]

PatchElements = Union[
    schemas.PatchElement,
    schemas.PatchElementCarrier,
    schemas.PatchSurfaceVehicle,
    schemas.PatchPropulsiveVehicle,
    schemas.PatchRoboticAgent,
    schemas.PatchHumanAgent,
    schemas.PatchResourceContainer,
=======
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
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
]

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


<<<<<<< HEAD
@router.get("/", response_model=List[Elements])
=======
@router.get(
    "/",
    response_model=List[ReadElements],
    description="List elements currently in the database.",
)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
def list_elements(
    skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.get(
<<<<<<< HEAD
    "/{id_}", response_model=Elements, responses=NOT_FOUND_RESPONSE,
=======
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Find a specific element in the database.",
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
)
def read_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


<<<<<<< HEAD
@router.post("/", response_model=Elements, status_code=status.HTTP_201_CREATED)
=======
@router.post(
    "/",
    response_model=ReadElements,
    status_code=status.HTTP_201_CREATED,
    description="Add a new element to the database.",
)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
def create_element(element: Elements, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


<<<<<<< HEAD
# TODO: PATCH requests are allowed to not have certain fields and only update the specified
#  fields. They also won't have the corresponding IDs, so they'll need a new schema


@router.patch("/{id_}", response_model=Elements)
def patch_element(
    id_: int, element: PatchElements, db: Session = Depends(database.get_db)
=======
@router.patch(
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Update an existing element in the database.",
)
def patch_element(
    id_: int, element: UpdateElements, db: Session = Depends(database.get_db)
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.delete(
<<<<<<< HEAD
    "/{id_}", response_model=Elements, responses=NOT_FOUND_RESPONSE,
=======
    "/{id_}",
    response_model=ReadElements,
    responses=NOT_FOUND_RESPONSE,
    description="Delete an element from the database.",
>>>>>>> a14263327e51c6b639d2ebd658e5b12615f88296
)
def delete_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")
