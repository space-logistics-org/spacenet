import json

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, strategies as st

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario
from ..main import app
from ..spatial_simulation import SimResult

pytestmark = [pytest.mark.integration, pytest.mark.analysis]

client = TestClient(app)


@given(scenario=st.builds(Scenario))
@pytest.mark.slow
@pytest.mark.xfail
def test_only_allowed_error_codes(scenario: Scenario):
    response = client.get("/simulation", json=json.loads(scenario.json()))
    assert 200 == response.status_code
    # for now 200 is the only acceptable status code;
    # may allow different status code for error case


@given(scenario=st.builds(Scenario))
@pytest.mark.slow
@pytest.mark.xfail
def test_same_result_as_analysis(scenario: Scenario):
    response = client.get("/simulation", json=json.loads(scenario.json()))
    sim = Simulation(scenario)
    expected_errors = sim.run()
    if expected_errors:
        assert response.json() == [error.json() for error in expected_errors]
    else:
        assert SimResult.parse_obj(response.json()) == SimResult.from_sim(sim)
