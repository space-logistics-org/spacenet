import pkg_resources
import pytest

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario


pytestmark = [pytest.mark.analysis, pytest.mark.apollo_17]


@pytest.mark.xfail(reason="simulation mvp not complete yet")
def test_scenario_runs_without_error():
    filename = pkg_resources.resource_filename("spacenet.schemas", "apollo_17/apollo_17.json")
    scenario = Scenario.parse_file(filename)
    errors = Simulation(scenario).run()
    assert len(errors) == 0, "expected no errors"
