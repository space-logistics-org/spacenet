import pytest

from hypothesis import given

from .utilities import build_checked_scenario
from ..checked_scenario import CheckedScenario
from ..simulation import Simulation
from ..exceptions import EventDateOverflowError, UnrecognizedID
from ...schemas import Scenario

pytestmark = [pytest.mark.schema, pytest.mark.unit, pytest.mark.analysis]


@pytest.mark.slow
@given(scenario=build_checked_scenario)
def test_build_validating_scenario_always_validates(scenario: CheckedScenario) -> None:
    CheckedScenario.parse_obj(scenario.dict())


ALLOWED_ERRORS_WHEN_CONSTRUCTING_SIM = (EventDateOverflowError, UnrecognizedID)


@pytest.mark.slow
@given(scenario=build_checked_scenario)
def test_build_validating_scenario_only_raises_some_errors(scenario: CheckedScenario):
    try:
        Simulation(scenario)
    except ALLOWED_ERRORS_WHEN_CONSTRUCTING_SIM:
        pass
