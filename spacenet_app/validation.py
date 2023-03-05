from fastapi import APIRouter, File, HTTPException, status, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from spacenet.schemas import Scenario


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