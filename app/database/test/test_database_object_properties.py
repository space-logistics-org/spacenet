from collections import defaultdict
from typing import Tuple, Type

import pytest
from hypothesis import assume, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, consumes, Bundle

from spacenet.schemas.constants import SQLITE_MIN_INT, SQLITE_MAX_INT
from .utilities import TestingSessionLocal, test_engine
from ..api import models
from ..api.database import Base
from ..api.models.utilities import MODEL_TO_PARENT, SCHEMA_TO_MODEL, dictify_row

pytestmark = [
    pytest.mark.unit,
    pytest.mark.edge,
    pytest.mark.element,
    pytest.mark.node,
    pytest.mark.resource,
    pytest.mark.state,
    pytest.mark.slow,
]


class DatabaseOperations(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.model = defaultdict(dict)
        self.db = TestingSessionLocal()

    # inserted IDs and the table of the inserted element
    inserted = Bundle("inserted")

    @rule(
        target=inserted,
        entry=st.one_of(*(st.builds(schema) for schema in SCHEMA_TO_MODEL.keys())),
    )
    def create(self, entry):
        model_cls = SCHEMA_TO_MODEL[type(entry)]
        if issubclass(model_cls, models.State):
            assume(entry.element_id in self.model[models.Element])
        db_object = model_cls(**entry.dict())
        self.db.add(db_object)
        self.db.commit()
        self.db.refresh(db_object)
        parent_model = MODEL_TO_PARENT[model_cls]
        as_dict = dictify_row(db_object)
        self.model[parent_model][db_object.id] = as_dict
        return db_object.id, parent_model

    @rule(id_and_table=inserted)
    def read(self, id_and_table: Tuple[int, Type]):
        id_, table = id_and_table
        from_db = self.db.query(table).get(id_)
        assert table in self.model
        assert id_ in self.model[table], f"Could not find {id_} in {table}"
        entry = self.model[table][id_]
        for attr, value in entry.items():
            assert hasattr(from_db, attr), f"Expected {attr} on {type(from_db)}"
            assert value == getattr(from_db, attr)

    @rule(
        id_=st.integers(min_value=SQLITE_MIN_INT, max_value=SQLITE_MAX_INT),
        table=st.sampled_from(list(MODEL_TO_PARENT.values())),
    )
    def read_invalid_id(self, id_, table):
        assume(id_ not in self.model[table])
        from_db = self.db.query(table).get(id_)
        assert from_db is None

    @rule(table=st.sampled_from(list(MODEL_TO_PARENT.values())))
    def read_all(self, table: Type):
        from_db = self.db.query(table).all()
        model_table = self.model[table]
        assert len(model_table) == len(from_db)
        for row in from_db:
            assert row.id in model_table
            assert model_table[row.id] == dictify_row(row)

    @rule(id_and_table=consumes(inserted))
    def delete(self, id_and_table: Tuple[int, Type]):
        id_, table = id_and_table
        from_db = self.db.query(table).get(id_)
        parent_model = MODEL_TO_PARENT[type(from_db)]
        if parent_model == models.Element:
            self.model[models.State] = {
                state_id: state
                for state_id, state in self.model[models.State]
                if state["element_id"] != id_
            }
        self.model[parent_model].pop(from_db.id)
        self.db.delete(from_db)
        self.db.commit()

    def teardown(self):
        Base.metadata.drop_all(test_engine, checkfirst=True)
        Base.metadata.create_all(test_engine, checkfirst=False)


TestDatabaseObjects = DatabaseOperations.TestCase
