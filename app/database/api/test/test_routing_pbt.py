from collections import defaultdict
from typing import Union

import pytest
import hypothesis.strategies as st
from fastapi.testclient import TestClient
from hypothesis import assume
from hypothesis.stateful import (
    RuleBasedStateMachine,
    consumes,
    rule,
    Bundle,
)

from spacenet.constants import SQLITE_MIN_INT, SQLITE_MAX_INT
from .utilities import get_test_db
from app.database.api import models
from app.database.api.database import get_db
from app.database.api.main import app
from ..schemas import *
from ..schemas.constants import (
    CREATE_TO_UPDATE,
    EDGE_SCHEMAS,
    ELEMENT_SCHEMAS,
    NODE_SCHEMAS,
    RESOURCE_SCHEMAS,
)
from ..models import utilities as model_utils
from ...test.utilities import test_engine

pytestmark = [
    pytest.mark.integration,
    pytest.mark.routing,
    pytest.mark.edge,
    pytest.mark.element,
    pytest.mark.node,
    pytest.mark.resource,
    pytest.mark.slow,
]

app.dependency_overrid_es[get_db] = get_test_db

TYPE_TO_PREFIX = {
    **{schema: "/edge" for schema in EDGE_SCHEMAS},
    **{schema: "/element" for schema in ELEMENT_SCHEMAS},
    **{schema: "/node" for schema in NODE_SCHEMAS},
    **{schema: "/resource" for schema in RESOURCE_SCHEMAS},
}


class DatabaseEditorCRUDRoutes(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = defaultdict(dict)
        self.client = TestClient(app)
        self.clear_tables()

    @classmethod
    def clear_tables(cls):
        for model in model_utils.MODEL_TO_PARENT.values():
            model.__table__.drop(test_engine, checkfirst=True)
            model.__table__.create(test_engine, checkfirst=False)

    inserted = Bundle("inserted")

    def create(self, create_schema):
        prefix = TYPE_TO_PREFIX[type(create_schema)]
        response = self.client.post(f"{prefix}/", json=create_schema.dict())
        assert 201 == response.status_code
        result = response.json()
        assert dict(create_schema.dict, id=result.get("id")) == result
        self.model[type(create_schema)][result.get("id")] = result
        # TODO: what should this return? The entire thing?

    def read(self, id_and_type):
        id_, type_ = id_and_type
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.get("/".join((prefix, id_)))
        assert 200 == response.status_code
        assert id_ in self.model[type_]
        assert self.model[type_][id_] == response.json()

    def read_invalid_id(self, id_and_type):
        id_, type_ = id_and_type
        assume(id_ not in self.model[type_])
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.get("/".join((prefix, id_)))
        assert 404 == response.status_code

    def read_all(self):
        for type_, entries in self.model.items():
            prefix = TYPE_TO_PREFIX[type_]
            response = self.client.get(f"{prefix}/")
            assert 200 == response.status_code
            result = response.json()
            assert len(entries) == len(result)
            for entry in result:
                id_ = entry.get("id")
                assert id_ in entries
                assert entries[id_] == entry

    def update(self, id_type_and_schema):
        id_, type_, update_schema = id_type_and_schema
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.patch("/".join((prefix, id_)), json=update_schema.dict())
        assert 200 == response.status_code
        # TODO: if storing entire objects on bundle, this has to consume

    def update_invalid_id(self, id_type_and_schema):
        id_, type_, update_schema = id_type_and_schema
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.patch("/".join((prefix, id_)), json=update_schema.dict())
        assert 404 == response.status_code

    def update_type_mismatch(self, id_type_and_schema):
        id_, type_, update_schema = id_type_and_schema
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.patch("/".join((prefix, id_)), json=update_schema.dict())
        assert 409 == response.status_code

    def delete(self, id_and_type):
        id_, type_ = id_and_type
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.delete("/".join((prefix, id_)))
        assert 200 == response.status_code
        result = response.json()
        assert self.model[type_].pop(result.get("id")) == result

    def delete_invalid_id(self, id_and_type):
        id_, type_ = id_and_type
        assume(id_ not in self.model[type_])
        prefix = TYPE_TO_PREFIX[type_]
        response = self.client.delete("/".join((prefix, id_)))
        assert 404 == response.status_code

    def teardown(self):
        self.clear_tables()


TestRouting = DatabaseEditorCRUDRoutes.TestCase
