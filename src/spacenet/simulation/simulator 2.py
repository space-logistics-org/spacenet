"""
Simulator.
"""

from datetime import datetime
from functools import total_ordering

from ..schemas import AllEvents, Mission, Scenario
from .state import State


@total_ordering
class ScheduledEvent:
    """
    Wrapper for events scheduled in a simulator.
    """

    def __init__(self, mission: Mission, event: AllEvents):
        self.time = mission.start_date + event.mission_time
        self.event = event

    def __lt__(self, other):
        return self.time <= other.time and self.event.priority < other.event.priority


class Simulator:
    """
    Simulator that executes events following a discrete event simulation.
    """

    def execute(self, scenario: Scenario, until: datetime = None) -> State:
        """
        Executes simulation of a scenario.

        Args:
            scenario (:obj:`Scenario`): The scenario to execute.
            until (:obj:`datetime.datetime`, Optional): The time to stop execution.

        Returns:

        """
        state = State(scenario)

        events = []
        for mission in scenario.mission_list:
            for event in mission.events:
                events.append(ScheduledEvent(mission, event))

        events = sorted(events)

        while len(events) > 0 and events[0].time <= until:
            event = events.pop()
            delta_t = state.time - event.time
            event.execute(state)
            # handle element demand models
