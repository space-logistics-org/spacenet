import json
from typing import Dict, Iterable

import pkg_resources
import pytest
from pydantic import ValidationError

from spacenet.analysis.checked_scenario import CheckedScenario


@pytest.fixture
def checked_scenario_regression_inputs() -> None:
    filename = pkg_resources.resource_filename(
        __name__, "checked_scenario_regression_inputs.json"
    )
    with open(filename) as f:
        yield json.load(f)


def test_checked_scenario_regression_inputs(
    checked_scenario_regression_inputs: Iterable[Dict],
) -> None:
    for inp in checked_scenario_regression_inputs:
        try:
            CheckedScenario.parse_obj(inp)
        except ValidationError:
            pass
