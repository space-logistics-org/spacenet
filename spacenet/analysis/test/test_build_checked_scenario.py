import pytest

from hypothesis import given

from .utilities import build_validating_scenario
from ..checked_scenario import CheckedScenario
from ...schemas import Scenario

pytestmark = [pytest.mark.schema, pytest.mark.unit]


@given(scenario=build_validating_scenario())
def test_build_validating_scenario_always_validates(scenario: Scenario) -> None:
    CheckedScenario.parse_obj(scenario.dict())
