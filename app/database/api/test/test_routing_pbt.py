from collections import defaultdict

import hypothesis.strategies as st
import pytest
from fastapi.testclient import TestClient
from hypothesis import assume
from hypothesis.stateful import Bundle, RuleBasedStateMachine, consumes, rule

from app.database.api import models
from app.database.api.database import Base, get_db
from app.database.api.main import app
from app.dependencies import current_user
from spacenet.constants import SQLITE_MAX_INT, SQLITE_MIN_INT
from spacenet.schemas import Element, State
from .utilities import get_current_user, get_test_db
from ..models import utilities as model_utils
from ..schemas.constants import CREATE_SCHEMAS, CREATE_TO_UPDATE
from ...test.utilities import test_engine

pytestmark = [
    pytest.mark.integration,
    pytest.mark.routing,
    pytest.mark.edge,
    pytest.mark.element,
    pytest.mark.node,
    pytest.mark.resource,
    pytest.mark.state,
    pytest.mark.slow,
]

app.dependency_overrides[get_db] = get_test_db
app.dependency_overrides[current_user] = get_current_user

PARENT_TO_PREFIX = {
    models.Edge: "/edge",
    models.Element: "/element",
    models.Node: "/node",
    models.Resource: "/resource",
    models.State: "/state",
}


def type_to_table(schema_cls):
    child_model = model_utils.SCHEMA_TO_MODEL[schema_cls]
    return model_utils.MODEL_TO_PARENT[child_model]


# Mapping from a given schema to the set of schemas in the same table as that schema,
# including the original provided schema
SCHEMAS_IN_SAME_TABLE = {
    first: {second}
    for first in model_utils.SCHEMA_TO_MODEL
    for second in model_utils.SCHEMA_TO_MODEL
    if type_to_table(first) == type_to_table(second)
}


class DatabaseEditorCRUDRoutes(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = defaultdict(dict)
        self.client = TestClient(app)
        self.clear_tables()

    @classmethod
    def clear_tables(cls):
        Base.metadata.drop_all(test_engine, checkfirst=True)
        Base.metadata.create_all(test_engine, checkfirst=False)

    inserted = Bundle("inserted")

    @rule(
        target=inserted,
        create_schema=st.one_of(*(st.builds(cls) for cls in CREATE_SCHEMAS)),
    )
    def create(self, create_schema):
        type_ = type(create_schema)
        if issubclass(type_, State):
            assume(create_schema.element_id in self.model[models.Element])
        table = type_to_table(type_)
        prefix = PARENT_TO_PREFIX[table]
        schema_dict = create_schema.dict()
        response = self.client.post(f"{prefix}/", json=schema_dict)
        assert 201 == response.status_code
        result = response.json()
        id_ = result.get("id")
        assert dict(schema_dict, id=id_) == result
        self.model[table][id_] = result
        return id_, type(create_schema)

    @rule(id_and_type=inserted)
    def read(self, id_and_type):
        id_, type_ = id_and_type
        table = type_to_table(type_)
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.get("/".join((prefix, str(id_))))
        assert 200 == response.status_code
        assert id_ in self.model[table]
        assert self.model[table][id_] == response.json()

    @rule(id_and_type=inserted)
    def read_invalid_id(self, id_and_type):
        id_, type_ = id_and_type
        table = type_to_table(type_)
        assume(id_ not in self.model[table])
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.get("/".join((prefix, str(id_))))
        assert 404 == response.status_code

    @rule()
    def read_all(self):
        for table, entries in self.model.items():
            prefix = PARENT_TO_PREFIX[table]
            response = self.client.get(f"{prefix}/")
            assert 200 == response.status_code
            result = response.json()
            assert len(entries) == len(result)
            for entry in result:
                id_ = entry.get("id")
                assert id_ in entries
                assert entries[id_] == entry

    @rule(
        id_type_and_schema=inserted.flatmap(
            lambda t: st.tuples(
                st.just(t[0]), st.just(t[1]), st.builds(CREATE_TO_UPDATE[t[1]])
            )
        )
    )
    def update(self, id_type_and_schema):
        id_, type_, update_schema = id_type_and_schema
        table = type_to_table(type_)
        prefix = PARENT_TO_PREFIX[table]
        update_dict = update_schema.dict()
        response = self.client.patch("/".join((prefix, str(id_))), json=update_dict)
        assert 200 == response.status_code
        self.model[table][id_] = dict(
            self.model[table][id_],
            **{k: v for k, v in update_dict.items() if v is not None},
        )
        assert self.model[table][id_] == response.json()

    @rule(
        id_type_and_schema=inserted.flatmap(
            lambda t: st.tuples(
                st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
                st.just(t[1]),
                st.builds(CREATE_TO_UPDATE[t[1]]),
            )
        )
    )
    def update_invalid_id(self, id_type_and_schema):
        id_, type_, update_schema = id_type_and_schema
        table = type_to_table(type_)
        assume(id_ not in self.model[table])
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.patch(
            "/".join((prefix, str(id_))), json=update_schema.dict()
        )
        assert 404 == response.status_code

    @rule(
        id_table_and_schema=inserted.flatmap(
            lambda t: st.tuples(
                st.just(t[0]),
                st.just(type_to_table(t[1])),
                st.one_of(
                    *(
                        st.builds(cls)
                        for cls in SCHEMAS_IN_SAME_TABLE[t[1]]
                        if cls != t[1]
                    )
                ),
            )
        )
    )
    def update_type_mismatch(self, id_table_and_schema):
        id_, table, update_schema = id_table_and_schema
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.patch(
            "/".join((prefix, str(id_))), json=update_schema.dict()
        )
        assert 409 == response.status_code

    @rule(id_and_type=consumes(inserted))
    def delete(self, id_and_type):
        id_, type_ = id_and_type
        table = type_to_table(type_)
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.delete("/".join((prefix, str(id_))))
        assert 200 == response.status_code
        result = response.json()
        assert self.model[table].pop(result.get("id")) == result
        if issubclass(
            type_, Element
        ):  # on element delete, also delete associated states
            states_to_delete = [
                id_
                for id_, state in self.model[models.State].items()
                if state["element_id"] == id_
            ]
            for state_id in states_to_delete:
                assert 404 == self.client.get(f"/state/{state_id}").status_code
                del self.model[models.State][state_id]

    @rule(
        id_and_type=inserted.flatmap(
            lambda t: st.tuples(
                st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
                st.just(t[1]),
            )
        )
    )
    def delete_invalid_id(self, id_and_type):
        id_, type_ = id_and_type
        table = type_to_table(type_)
        assume(id_ not in self.model[table])
        prefix = PARENT_TO_PREFIX[table]
        response = self.client.delete("/".join((prefix, str(id_))))
        assert 404 == response.status_code

    def teardown(self):
        self.clear_tables()


TestRouting = DatabaseEditorCRUDRoutes.TestCase
