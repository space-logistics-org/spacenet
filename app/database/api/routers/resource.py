from fastapi import APIRouter

router = APIRouter()
UNIMPLEMENTED = {"message": "unimplemented"}


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
    Find the record associated with the resource with id "id".

    :param id_: the id of the record to find
    :return: the record associated with the resource with id "id"
    """
    return UNIMPLEMENTED


@router.post("/")
async def add_resource():
    """
    Add the resource described in the request to the database.

    :return: (not known yet?)
    """
    return UNIMPLEMENTED


@router.patch("/{id_}")
async def update_record(id_: int):
    """
    Update the record associated with the resource with id "id".

    :param id_: the id of the record to find
    :return: (not known yet?)
    """
    return UNIMPLEMENTED


@router.delete("/{id_}")
async def delete_record(id_: int):
    """
    Delete the record associated with the resource with id "id".

    :param id_: the id of the record to find
    :return: (not known yet?)
    """
    return UNIMPLEMENTED
