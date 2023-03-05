"""
This module contains stateful tests that the database behaves similarly to a dictionary for
inserting solely resources.
"""
from typing import Union

import hypothesis.strategies as st
import pytest
from fastapi.testclient import TestClient
from hypothesis import assume
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, rule

from ..database import get_db
from ..main import app
from ..models.resource import Resource as ResourceModel
from .utilities import test_engine
from ....auth_dependencies import current_user
from spacenet.schemas.constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from .utilities import get_current_user, get_test_db
from ..schemas.constants import CREATE_TO_UPDATE
from ..schemas.resource import (
    ContinuousResource,
    DiscreteResource,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.resource,
    pytest.mark.routing,
    pytest.mark.slow,
]

app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[current_user] = get_current_user


def inserted_tup_to_strategy(inserted_tup):
    """
    Convert a tuple of inserted values into a strategy for updating that inserted value.

    :param inserted_tup: tuple inserted: id and type of inserted value
    :return: a strategy for updating the inserted value
    """
    id_, type_ = inserted_tup
    update_type = CREATE_TO_UPDATE[type_]
    return st.tuples(st.just(id_), st.builds(update_type).map(update_type.dict))


class ResourceRoutes(RuleBasedStateMachine):
    """
    A class defining a stateful test for resource routes.
    """
    def __init__(self):
        super().__init__()
        self.model = {}
        self.client = TestClient(app)

    inserted = Bundle("inserted")  # tuples of id and type

    @rule(
        target=inserted,
        entry=st.one_of(
            *(st.builds(cls) for cls in (ContinuousResource, DiscreteResource))
        ),
    )
    def create(self, entry: Union[ContinuousResource, DiscreteResource]):
        """
        Create a new resource entry.
        """
        response = self.client.post("/resource/", json=entry.dict())
        assert 201 == response.status_code
        result = response.json()
        assert dict(entry, id=result.get("id")) == result
        self.model[result.get("id")] = result
        # Add the ID provided by the database to the bundle of inserted IDs
        return result.get("id"), type(entry)

    @rule(id_and_type=inserted)
    def read(self, id_and_type):
        """
        Read an existing resource entry.
        """
        id_, _ = id_and_type
        response = self.client.get(f"/resource/{id_}")
        assert 200 == response.status_code
        assert self.model[id_] == response.json()

    @rule(id_=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT))
    def read_invalid_id(self, id_):
        """
        Attempt to read a nonexistent resource entry.
        """
        assume(id_ not in self.model)
        response = self.client.get(f"/resource/{id_}")
        assert 404 == response.status_code

    @rule()
    def read_all(self):
        """
        Read all resource entries.
        """
        response = self.client.get("/resource/")
        assert 200 == response.status_code
        result = response.json()
        assert len(self.model) == len(result)
        for resource in result:
            assert (
                resource.get("id") in self.model
            ), f"{resource.get('id')} in response but not in model"
            assert self.model[resource.get("id")] == resource

    @rule(id_and_kwargs=inserted.flatmap(inserted_tup_to_strategy))
    def update(self, id_and_kwargs):
        """
        Update an existing resource entry.
        """
        id_, update_kwargs = id_and_kwargs
        response = self.client.patch(f"/resource/{id_}", json=update_kwargs)
        assert 200 == response.status_code
        self.model[id_] = dict(
            self.model[id_], **{k: v for k, v in update_kwargs.items() if v is not None}
        )
        assert self.model[id_] == response.json()

    @rule(
        id_=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
        kwargs=inserted.flatmap(inserted_tup_to_strategy).map(lambda t: t[1]),
    )
    def update_invalid_id(self, id_, kwargs):
        """
        Attempt to update an existing resource entry via an invalid ID.
        """
        assume(id_ not in self.model)
        response = self.client.patch(f"/resource/{id_}", json=kwargs)
        assert 404 == response.status_code

    @rule(id_and_type=consumes(inserted))
    def delete(self, id_and_type):
        """
        Delete an existing resource entry.
        """
        id_, _ = id_and_type
        response = self.client.delete(f"/resource/{id_}")
        assert 200 == response.status_code
        result = response.json()
        assert self.model.pop(result.get("id")) == result

    @rule(id_=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT))
    def delete_invalid_id(self, id_):
        """
        Attempt to delete an existing resource entry via an invalid ID.
        """
        assume(id_ not in self.model)
        response = self.client.delete(f"/resource/{id_}")
        assert 404 == response.status_code

    def teardown(self):
        """
        Clear the existing test tables.
        :return:
        """
        ResourceModel.__table__.drop(test_engine, checkfirst=True)
        ResourceModel.__table__.create(test_engine, checkfirst=False)


TestResourceRoutes = ResourceRoutes.TestCase
