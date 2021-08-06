import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import assume, given

from spacenet.analysis.exceptions import SimException
from spacenet.analysis.simulation import Simulation
from spacenet.analysis.test.utilities import build_validating_scenario
from spacenet.schemas import Scenario
from ..main import app
from ..spatial_simulation import ResultAndErrors

pytestmark = [pytest.mark.integration, pytest.mark.analysis]

client = TestClient(app)


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=build_validating_scenario())
def test_only_allowed_status_codes(scenario: Scenario):
    response = client.post("/simulation/", json=jsonable_encoder(scenario.dict()))
    if response.status_code == 422:  # TODO: change this when 422 is no longer returned
        try:
            Simulation(scenario)
        except SimException:
            return
        else:
            assert False
    assert response.status_code == 200


@pytest.mark.slow
@pytest.mark.xfail
@given(scenario=build_validating_scenario())
def test_same_result_as_analysis(scenario: Scenario):
    response = client.post("/simulation/", json=jsonable_encoder(scenario.dict()))
    response_json = response.json()
    try:
        sim = Simulation(scenario)
    except SimException:
        assume(False)
        return
    sim.run()
    assert ResultAndErrors(
        result=sim.result(), errors=sim.errors
    ) == ResultAndErrors.parse_obj(response_json)
