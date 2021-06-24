"""
Tests for resource routing using rule-based state machines as implemented by Hypothesis.
Operations exercised:
- create
    add a resource which is correctly constructed
- create_invalid
    add a resource which is not correctly constructed
- read
    read a resource already present
- read_not_present
    read a resource not inserted
- read_all
    read all resources
- update
    update a resource already present
- update_not_present
    update a resource at an ID not inserted
- update_invalid
    update a resource with invalid schema at an already-inserted ID
- update_wrong_type
    update a resource with a valid schema in a way that changes the object's type
- delete
    delete a resource already present
- delete_not_present
    delete a resource not present
Bundles:
- inserted_ids
    stores inserted ids for use in valid operations
"""
from typing import Union

import pytest
import hypothesis.strategies as st
from fastapi.testclient import TestClient
from hypothesis.stateful import (
    RuleBasedStateMachine,
    consumes,
    rule,
    Bundle,
    precondition,
)

from .utilities import override_get_db
from app.database.api.database import get_db
from app.database.api.main import app
from ..schemas.resource import (
    ContinuousResource,
    ContinuousRead,
    DiscreteResource,
    DiscreteRead,
)

pytestmark = [pytest.mark.integration, pytest.mark.resource, pytest.mark.routing]

app.dependency_overrides[get_db] = override_get_db


class ResourceRoutes(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = {}
        self.client = TestClient(app)

    inserted_ids = Bundle("inserted_ids")

    @rule(
        target=inserted_ids,
        entry=st.one_of(
            st.builds(ContinuousResource).map(ContinuousResource.dict),
            st.builds(DiscreteResource).map(DiscreteResource.dict),
        ),
    )
    def create(self, entry: Union[ContinuousResource, DiscreteResource]):
        response = self.client.post("/resource/", json=entry)
        assert 201 == response.status_code
        result = response.json()
        assert {**entry, "id": result.get("id")} == result
        self.model[result.get("id")] = result
        return result.get("id")

    @rule(id_=inserted_ids)
    def read(self, id_):
        response = self.client.get(f"/resource/{id_}")
        assert 200 == response.status_code
        result = response.json()
        assert self.model[result.get("id")] == result

    @rule(id_=consumes(inserted_ids))
    def delete(self, id_):
        response = self.client.delete(f"/resource/{id_}")
        assert 200 == response.status_code
        result = response.json()
        assert self.model[result.get("id")] == result
        del self.model[result.get("id")]


TestResourceRoutes = ResourceRoutes.TestCase
