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
from ..schemas.constants import CREATE_TO_UPDATE
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


class TestRouting(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = defaultdict(set)
        self.client = TestClient(app)
        self.clear_tables()

    @classmethod
    def clear_tables(cls):
        for model in model_utils.MODEL_TO_PARENT.values():
            model.__table__.drop(test_engine, checkfirst=True)
            model.__table__.create(test_engine, checkfirst=False)

    inserted = Bundle("inserted")

    def create(self, create_schema):
        pass

    def read(self, id_and_type):
        pass
    
    def read_invalid_id(self, id_and_type):
        pass
    
    def read_all(self):
        pass

    def update(self, id_type_and_schema):
        pass

    def update_invalid_id(self, id_and_type):
        pass

    def update_type_mismatch(self, id_type_and_schema):
        pass

    def delete(self, id_and_type):
        pass

    def delete_invalid_id(self, id_and_type):
        pass

    def teardown(self):
        self.clear_tables()
