from typing import Union

import pytest
import hypothesis.strategies as st
from fastapi.testclient import TestClient
from hypothesis.stateful import (
    RuleBasedStateMachine,
    consumes,
    rule,
    Bundle,
)

from .utilities import get_test_db
from app.database.api.database import get_db
from app.database.api.main import app
from ..schemas.resource import (
    ContinuousResource,
    ContinuousUpdate,
    DiscreteResource,
)

pytestmark = [pytest.mark.integration, pytest.mark.resource, pytest.mark.routing]

app.dependency_overrides[get_db] = get_test_db


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
        # Add the ID provided by the database to the bundle of inserted IDs
        return result.get("id")

    @rule(id_=inserted_ids)
    def read(self, id_):
        response = self.client.get(f"/resource/{id_}")
        assert 200 == response.status_code
        result = response.json()
        assert self.model[id_] == result

    @rule()
    def read_all(self):
        response = self.client.get("/resource/")
        assert 200 == response.status_code
        for resource in response.json():
            assert (
                resource.get("id") in self.model
            ), f"{resource.get('id')} in response but not in model"
            assert self.model[resource.get("id")] == resource

    @rule(
        id_=inserted_ids,
        update_kwargs=st.builds(ContinuousUpdate).map(
            lambda schema: {k: v for k, v in schema.dict().items() if k != "type"}
        ),
    )
    def update(self, id_, update_kwargs):
        update_kwargs = {**update_kwargs, "type": self.model.get(id_).get("type")}
        response = self.client.patch(f"/resource/{id_}", json=update_kwargs)
        assert 200 == response.status_code, response.json()
        self.model[id_] = {
            **self.model[id_],
            **{k: v for k, v in update_kwargs.items() if v is not None},
        }
        assert self.model[id_] == response.json()

    @rule(id_=consumes(inserted_ids))
    def delete(self, id_):
        response = self.client.delete(f"/resource/{id_}")
        assert 200 == response.status_code
        result = response.json()
        assert self.model.pop(result.get("id")) == result

    def teardown(self):
        for id_, expected in self.model.items():
            response = self.client.delete(f"/resource/{id_}")
            assert 200 == response.status_code
            assert expected == response.json()


TestResourceRoutes = ResourceRoutes.TestCase
