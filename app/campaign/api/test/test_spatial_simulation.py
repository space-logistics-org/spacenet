import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import given, strategies as st

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario
from ..main import app
from ..spatial_simulation import SimResult

pytestmark = [pytest.mark.integration, pytest.mark.analysis]

client = TestClient(app)


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=st.builds(Scenario))
def test_only_allowed_status_codes(scenario: Scenario):
    response = client.get("/simulation", json=jsonable_encoder(scenario.dict()))
    assert 200 == response.status_code
    # for now 200 is the only acceptable status code;
    # may allow different status code for error case


def error_case(response_json, sim_errors):
    assert response_json == [error.json() for error in sim_errors]


def success_case(response_json, sim):
    assert SimResult.parse_obj(response_json) == sim.result(), response_json


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=st.builds(Scenario))
def test_same_result_as_analysis(scenario: Scenario):
    response = client.get("/simulation", json=jsonable_encoder(scenario.dict()))
    response_json = response.json()
    sim = Simulation(scenario)
    sim.run()
    expected_errors = sim.errors
    if expected_errors:
        error_case(response_json, expected_errors)
    else:
        success_case(response_json, sim)
