from typing import Union

from fastapi import APIRouter
from spacenet.schemas import element

router = APIRouter()
UNIMPLEMENTED = {"message": "unimplemented"}

# TODO: this might work, but you'll have to manually type-check all of them, or support
#  operations on them from base class & just call the operation. How to resolve?
ElementKinds = Union[element.Element, element.ResourceContainer, element.ElementCarrier,
                     element.PropulsiveVehicle, element.SurfaceVehicle, element.RoboticAgent,
                     element.HumanAgent]


@router.get("/")
async def list_records():
    """
    List the records of all resources.

    :return: the list of the records of all resources
    """
    return UNIMPLEMENTED


# TODO: expected behavior when no associated ID or just invalid, but well-formed input? POST
#  return values are also not known

@router.get("/{id_}")
async def find_record(id_: int):
    """
    Find the record associated with the element with id "id_".

    :param id_: the id of the record to find
    :return: the record associated with the element with id "id_"
    """
    return UNIMPLEMENTED


@router.post("/")
async def add_resource(element: ElementKinds):
    """
    Add the element described in the request to the database.

    :param element: the information to associate with the new record
    :return: (not known yet?)
    """
    return UNIMPLEMENTED


@router.patch("/{id_}")
async def update_record(id_: int, element: ElementKinds):
    """
    Update the record associated with the element with id "id_".

    :param element: the new information to associate with the record
    :param id_: the id of the record to find
    :return: (not known yet?)
    """
    return UNIMPLEMENTED


@router.delete("/{id_}")
async def delete_record(id_: int):
    """
    Delete the record associated with the element with id "id_".

    :param id_: the id of the record to find
    :return: (not known yet?)
    """
    return UNIMPLEMENTED
