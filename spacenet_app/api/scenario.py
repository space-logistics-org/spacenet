"""
Endpoints to validate scenarios and load model databases.
"""

import tempfile

from fastapi import APIRouter, UploadFile

from spacenet.io import ModelDatabase, load_db
from spacenet.schemas import Scenario
from spacenet.simulation import State

from .models import ScenarioRequest

router = APIRouter()


@router.post("/scenario/validate")
def validate_scenario(request: ScenarioRequest) -> Scenario:
    """
    Validates a scenario and returns it in normalized form. Responds with
    status 422 if the scenario does not match the object schema or contains
    references to unknown objects.
    """
    State(request.scenario)
    return request.scenario


@router.post("/library/database")
def load_database(upload: UploadFile) -> ModelDatabase:
    """
    Loads a model database (nodes, edges, resources, element templates, and
    demand models) from a spreadsheet (Excel) file.
    """
    # write the uploaded file to a temporary file
    # https://bugs.python.org/issue26175
    with tempfile.TemporaryFile() as temp_file:
        temp_file.write(upload.file.read())
        temp_file.seek(0)
        try:
            return load_db(temp_file)
        except ValueError:
            raise
        except Exception as error:
            raise ValueError(f"Invalid model database: {error}") from error
