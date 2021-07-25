import pytest
from hypothesis import given
from pydantic import ValidationError

from .utilities import VALID_PRIORITIES, INVALID_PRIORITIES
from spacenet.schemas import Event


pytestmark = [pytest.mark.unit, pytest.mark.event, pytest.mark.schema]


@given(priority=VALID_PRIORITIES)
def test_valid_priority(priority):
    assert priority == Event(priority=priority).priority


@given(priority=INVALID_PRIORITIES)
def test_invalid_priority(priority):
    with pytest.raises(ValidationError):
        Event(priority=priority)
