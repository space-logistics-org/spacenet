import pkg_resources
import pytest

from pydantic import parse_file_as

from spacenet.analysis.simulation import Simulation
from spacenet.schemas import Scenario


pytestmark = [pytest.mark.analysis, pytest.mark.apollo_17]


@pytest.mark.xfail(reason="apollo 17 data doesn't match schema at present")
def test_scenario_parses():
    filename = pkg_resources.resource_filename("spacenet.schemas", "apollo_17/apollo_17.json")
    scenario = parse_file_as(Scenario, filename)
    assert len(Simulation(scenario).run()) == 0, "expected no errors"
