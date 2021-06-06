from typing import List, Union

from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from .. import database
from spacenet.schemas import element as schemas

router = APIRouter()

Elements = Union[
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
]

NOT_FOUND_RESPONSE = {status.HTTP_404_NOT_FOUND: {"msg": str}}


@router.get("/", response_model=List[Elements])
def list_elements(
    skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.get(
    "/{id_}", response_model=Elements, responses=NOT_FOUND_RESPONSE,
)
def read_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.post("/", response_model=Elements, status_code=status.HTTP_201_CREATED)
def create_element(element: Elements, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")


# TODO: PATCH requests are allowed to not have certain fields and only update the specified
#  fields. They also won't have the corresponding IDs, so they'll need a new schema


@router.patch("/{id_}", response_model=Elements)
def patch_element(
    id_: int, element: PatchElements, db: Session = Depends(database.get_db)
):
    raise HTTPException(status_code=500, detail="unimplemented")


@router.delete(
    "/{id_}", response_model=Elements, responses=NOT_FOUND_RESPONSE,
)
def delete_element(id_: int, db: Session = Depends(database.get_db)):
    raise HTTPException(status_code=500, detail="unimplemented")
