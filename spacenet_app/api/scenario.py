"""
Endpoints to validate scenarios and load model databases.
"""

import tempfile
from enum import Enum
from typing import get_args

from fastapi import APIRouter, Body, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from spacenet import schemas as s
from spacenet.io import ModelDatabase, load_db
from spacenet.schemas import Scenario
from spacenet.simulation import State

from .models import ScenarioRequest

router = APIRouter()


class ModelKind(str, Enum):
    """
    Enumeration of the kinds of object models of a library.
    """

    NODES = "nodes"
    EDGES = "edges"
    RESOURCES = "resources"
    ELEMENTS = "elements"
    DEMAND_MODELS = "demandModels"


def _by_type(union) -> dict:
    """Maps the value of the `type` field to each schema of a union."""
    return {
        getattr(schema.model_fields["type"].default, "value", None): schema
        for schema in get_args(union)
    }


#: Schemas of each kind of object model by the value of their `type` field.
MODEL_SCHEMAS = {
    ModelKind.NODES: _by_type(s.AllNodes),
    ModelKind.EDGES: _by_type(s.AllEdges),
    ModelKind.RESOURCES: _by_type(s.AllResources),
    ModelKind.ELEMENTS: _by_type(s.AllElements),
    ModelKind.DEMAND_MODELS: _by_type(s.AllDemandModels),
}


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


@router.post("/library/{kind}/validate")
def validate_model(kind: ModelKind, model: dict = Body(..., embed=True)):
    """
    Validates an object model (a node, an edge, a resource, an element
    template, or a demand model) and returns it in normalized form. Responds
    with status 422 if the model does not match the object schema of its type.
    """
    schema = MODEL_SCHEMAS[kind].get(model.get("type"))
    if schema is None:
        raise ValueError(f"Unknown type of {kind.value}: {model.get('type')}")
    try:
        return schema.model_validate(model)
    except ValidationError as error:
        return JSONResponse(
            status_code=422,
            content={
                "detail": jsonable_encoder(
                    error.errors(
                        include_url=False, include_context=False, include_input=False
                    )
                )
            },
        )
