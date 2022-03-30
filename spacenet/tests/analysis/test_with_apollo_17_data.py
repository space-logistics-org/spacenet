"""
This module contains tests that the Apollo 17 schema can be simulated without errors.
"""
from datetime import datetime

import pkg_resources
import pytest
from hypothesis import assume, given, strategies as st

from spacenet.analysis.checked_scenario import CheckedScenario
from spacenet.analysis.simulation import Simulation


pytestmark = [pytest.mark.analysis, pytest.mark.apollo_17]


def test_scenario_runs_without_error():
    filename = pkg_resources.resource_filename(
        "spacenet.schemas", "apollo_17/apollo_17.json"
    )
    scenario = CheckedScenario.parse_file(filename)
    sim = Simulation(scenario)
    sim.run()
    assert not sim.errors, "expected no errors"


@given(st.datetimes())
def test_scenario_runs_without_error_for_any_until(dt: datetime):
    filename = pkg_resources.resource_filename(
        "spacenet.schemas", "apollo_17/apollo_17.json"
    )
    scenario = CheckedScenario.parse_file(filename)
    sim = Simulation(scenario)
    sim.run(until=dt)
    assert not sim.errors, "expected no errors"


@given(st.datetimes())
def test_identical_result_for_datetime_after_last_event(dt: datetime):
    filename = pkg_resources.resource_filename(
        "spacenet.schemas", "apollo_17/apollo_17.json"
    )
    scenario = CheckedScenario.parse_file(filename)
    sim = Simulation(scenario)
    sim.run()
    assume(dt >= sim.current_time)
    stopping_sim = Simulation(scenario)
    stopping_sim.run(until=dt)
    assert sim.result == stopping_sim.result
