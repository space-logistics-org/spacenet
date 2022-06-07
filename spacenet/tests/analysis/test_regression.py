"""
This module contains regression tests for defined schemas that should parse and execute without
error.
"""
import os
from datetime import datetime

import pkg_resources
import pytest
from hypothesis import assume, given, strategies as st

from spacenet.analysis.checked_scenario import CheckedScenario
from spacenet.analysis.simulation import Simulation


pytestmark = [pytest.mark.analysis, pytest.mark.regression]


@given(st.booleans())
def test_scenario_runs_without_error(propulsive: bool):
    for filename in pkg_resources.resource_listdir("spacenet.analysis",
                                                   "test/regression_inputs"):
        path = pkg_resources.resource_filename("spacenet.analysis",
                                               f"test/regression_inputs/{filename}")
        scenario = CheckedScenario.parse_file(path)
        sim = Simulation(scenario, propulsive=propulsive)
        sim.run()
        assert not sim.errors, "expected no errors"


@given(st.datetimes(), st.booleans())
def test_scenario_runs_without_error_for_any_until(dt: datetime, propulsive: bool):
    for filename in pkg_resources.resource_listdir("spacenet.analysis",
                                                       "test/regression_inputs"):
        path = pkg_resources.resource_filename("spacenet.analysis",
                                               f"test/regression_inputs/{filename}")
        scenario = CheckedScenario.parse_file(path)
        sim = Simulation(scenario, propulsive=propulsive)
        sim.run(until=dt)
        assert not sim.errors, "expected no errors"


@given(st.datetimes(), st.booleans())
@pytest.mark.xfail(reason="TODO:figure out this bug")
def test_identical_result_for_datetime_after_last_event(dt: datetime, propulsive: bool):
    for filename in pkg_resources.resource_listdir("spacenet.analysis",
                                                   "test/regression_inputs"):
        path = pkg_resources.resource_filename("spacenet.analysis",
                                               f"test/regression_inputs/{filename}")
        scenario = CheckedScenario.parse_file(path)
        sim = Simulation(scenario)
        sim.run()
        assume(dt > sim.current_time)
        stopping_sim = Simulation(scenario, propulsive=propulsive)
        stopping_sim.run(until=dt)
        assert sim.result == stopping_sim.result
