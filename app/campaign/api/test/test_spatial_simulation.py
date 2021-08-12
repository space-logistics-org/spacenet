import pytest
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from hypothesis import assume, given, strategies as st

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
    # TODO: figure out the whole problem w/ providing unrealistically large floats. undo a
    #  register_type_strategy?
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
@given(scenario=build_validating_scenario(), propulsive=st.booleans())
def test_same_result_as_analysis(scenario: Scenario, propulsive: bool):
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
        result=sim.result(), errors=sim.errors
    ) == response_result
