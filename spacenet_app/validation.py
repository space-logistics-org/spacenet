import tempfile

from fastapi import APIRouter, File, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from spacenet.schemas import Scenario
from spacenet.io import load_db, ModelDatabase


router = APIRouter()


@router.post("/scenario")
async def validate_scenario_file(upload: UploadFile) -> Scenario:
    """
    Endpoint to validate a scenario in JSON format.
    Args:
        upload (UploadFile): User uploaded scenario JSON file.
    Returns:
        Scenario: Validated scenario.
    """
    contents = await upload.read()
    try:
        return Scenario.parse_raw(contents)
    except ValidationError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": error.errors()}),
        )


@router.post("/database")
async def validate_database_file(upload: UploadFile) -> ModelDatabase:
    """
    Endpoint to validate a database in Excel format.
    Args:
        upload (UploadFile): User uploaded database Excel file.
    Returns:
        ModelDatabase: Validated model database.
    """
    try:
        # due to known bug, write the uploaded file to a temporary file
        # https://bugs.python.org/issue26175
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(await upload.read())
            temp_file.seek(0)
            return load_db(temp_file)
    except ValueError as error:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": str(error)}),
        )
