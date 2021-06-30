"""
Property-based tests for the interactions between states and elements, namely that the foreign
key relation works correctly.
"""
from typing import Union

import pytest
from hypothesis import assume, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

from .utilities import TestingSessionLocal, test_engine
from ..api import models
from ..api.schemas.constants import CREATE_SCHEMAS, ELEMENT_SCHEMAS, STATE_SCHEMAS
from ..api.models.utilities import SCHEMA_TO_MODEL, dictify_row
from spacenet.schemas import Element, State

pytestmark = [
    pytest.mark.unit,
    pytest.mark.database,
    pytest.mark.element,
    pytest.mark.state,
    pytest.mark.slow,
]


def state_with_element_id(state: State, element_id: int):
    return type(state).parse_obj({**state.dict(), "element_id": element_id})


class ElementStateInteraction(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.db = TestingSessionLocal()
        self.elements = {}
        self.states = {}

    inserted_elements = Bundle("elements")

    def _create(self, entry: Union[Element, State]):
        model_cls = SCHEMA_TO_MODEL[type(entry)]
        db_entry = model_cls(**entry.dict())
        self.db.add(db_entry)
        self.db.commit()
        self.db.refresh(db_entry)
        as_dict = dictify_row(db_entry)
        table = self.states if isinstance(entry, State) else self.elements
        table[db_entry.id] = as_dict
        return db_entry.id

    @rule(
        target=inserted_elements,
        element=st.one_of(
            *(
                st.builds(element_cls)
                for element_cls in CREATE_SCHEMAS & ELEMENT_SCHEMAS
            )
        ),
    )
    def create_element(self, element: Element):
        return self._create(element)

    # element id must reference an element which exists in the database, hence the complex
    # flatmap
    @rule(
        state=inserted_elements.flatmap(
            lambda element_id: st.one_of(
                *(
                    st.builds(state_cls).map(
                        lambda state: state_with_element_id(state, element_id)
                    )
                    for state_cls in CREATE_SCHEMAS & STATE_SCHEMAS
                )
            )
        ),
    )
    def create_state(self, state: State):
        return self._create(state)

    @rule(element_id=st.integers())
    def delete_element(self, element_id):
        assume(element_id in self.elements)
        # Associated states should be deleted too
        from_db = self.db.query(models.Element).get(element_id)
        assert self.elements.pop(element_id) == dictify_row(from_db)
        self.db.delete(from_db)
        self.db.commit()
        states_to_delete = []
        for state_id, state in self.states.items():
            if state["element_id"] == element_id:
                query_result = self.db.query(models.State).get(state_id)
                assert query_result is None, (
                    f"Expected cascading delete but row was still present: "
                    f"{dictify_row(query_result)}"
                )
                states_to_delete.append(state_id)
        for state_id in states_to_delete:
            del self.states[state_id]

    @rule(state_id=st.integers())
    def delete_state(self, state_id):
        assume(state_id in self.states)
        from_db = self.db.query(models.State).get(state_id)
        assert self.states.pop(state_id) == dictify_row(from_db)
        self.db.delete(from_db)
        self.db.commit()

    @rule()
    def read_all_elements(self):
        self.read_all(models.Element, self.elements)

    @rule()
    def read_all_states(self):
        self.read_all(models.State, self.states)

    def read_all(self, table, mapping):
        from_db = self.db.query(table).all()
        assert len(mapping) == len(from_db)
        for row in from_db:
            assert row.id in mapping
            assert mapping[row.id] == dictify_row(row)

    def teardown(self):
        for table in (models.State, models.Element):
            table.__table__.drop(test_engine, checkfirst=True)
            table.__table__.create(test_engine, checkfirst=False)


TestElementStateInteraction = ElementStateInteraction.TestCase
