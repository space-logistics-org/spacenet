import pkg_resources
import pytest

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario


pytestmark = [pytest.mark.analysis, pytest.mark.apollo_17]


def test_scenario_runs_without_error():
    filename = pkg_resources.resource_filename("spacenet.schemas", "apollo_17/apollo_17.json")
    scenario = Scenario.parse_file(filename)
    sim = Simulation(scenario)
    sim.run()
    assert not sim.errors, "expected no errors"
