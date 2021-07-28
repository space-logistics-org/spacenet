import pkg_resources
import pytest

from .. import Scenario


pytestmark = [pytest.mark.schema, pytest.mark.apollo_17]


def test_scenario_parses():
    filename = pkg_resources.resource_filename("spacenet.schemas", "apollo_17/apollo_17.json")
    Scenario.parse_file(filename)
