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

    inserted = Bundle("inserted")

    def create(self, create_schema):
        pass

    def read(self, id_and_type):
        pass
    
    def read_invalid_id(self, id_and_type):
        pass
    
    def read_all(self):
        pass

    def update(self, id_, update_schema):
        pass

    def update_invalid_id(self, id_, update_schema):
        pass

    def delete(self, id_and_type):
        pass

    def delete_invalid_id(self, id_and_type):
        pass
