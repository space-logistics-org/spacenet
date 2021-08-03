import pytest

from hypothesis import given

from .utilities import build_validating_scenario
from ..checked_scenario import CheckedScenario
from ..simulation import Simulation
from ..exceptions import EventDateOverflowError, UnrecognizedID
from ...schemas import Scenario

pytestmark = [pytest.mark.schema, pytest.mark.unit, pytest.mark.analysis]


@given(scenario=build_validating_scenario())
def test_build_validating_scenario_always_validates(scenario: Scenario) -> None:
    CheckedScenario.parse_obj(scenario.dict())


ALLOWED_ERRORS_WHEN_CONSTRUCTING_SIM = (EventDateOverflowError, UnrecognizedID)


@given(scenario=build_validating_scenario())
def test_build_validating_scenario_only_raises_some_errors(scenario: Scenario):
    try:
        Simulation(scenario)
    except ALLOWED_ERRORS_WHEN_CONSTRUCTING_SIM:
        pass
