"""
This module defines tests for API routes used for analysis of campaigns via spatial simulation.
"""
import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import assume, given, strategies as st

from spacenet.analysis.checked_scenario import CheckedScenario
from spacenet.analysis.exceptions import SimException
from spacenet.analysis.simulation import Simulation
from spacenet.analysis.test.utilities import build_checked_scenario
from ..main import app
from ..spatial_simulation import ResultAndErrors

pytestmark = [pytest.mark.integration, pytest.mark.analysis]

client = TestClient(app)


@pytest.mark.slow
@given(scenario=build_checked_scenario)
def test_only_allowed_status_codes(scenario: CheckedScenario):
    response = client.post("/simulation/", json=jsonable_encoder(scenario.dict()))
    assert response.status_code in {200, 422}


@pytest.mark.slow
@given(scenario=build_checked_scenario, propulsive=st.booleans())
def test_same_result_as_analysis(scenario: CheckedScenario, propulsive: bool):
    try:
        sim = Simulation(scenario, propulsive=propulsive)
    except SimException:
        assume(False)
        return
    sim.run()
    response = client.post(
        f"/simulation/?propulsive={propulsive}", json=jsonable_encoder(scenario.dict())
    )
    response_result = ResultAndErrors.parse_obj(response.json())
    assert ResultAndErrors(
        result=sim.result, errors=sim.errors
    ) == response_result
