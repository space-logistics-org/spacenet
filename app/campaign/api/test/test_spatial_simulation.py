import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import assume, given, strategies as st

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario
from ..main import app
from ..spatial_simulation import ResultAndErrors

pytestmark = [pytest.mark.integration, pytest.mark.analysis]

client = TestClient(app)


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=st.builds(Scenario))
def test_only_allowed_status_codes(scenario: Scenario):
    response = client.post("/simulation", json=jsonable_encoder(scenario.dict()))
    assert 200 == response.status_code
    # for now 200 is the only acceptable status code;
    # may allow different status code for error case


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=st.builds(Scenario))
def test_same_result_as_analysis(scenario: Scenario):
    response = client.post("/simulation", json=jsonable_encoder(scenario.dict()))
    response_json = response.json()
    try:
        sim = Simulation(scenario)
    except ValueError:
        assume(False)
        return
    sim.run()
    assert ResultAndErrors(result=sim.result(), errors=sim.errors) == response_json
