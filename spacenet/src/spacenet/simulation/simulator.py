"""
Simulator.
"""

from functools import total_ordering

from ..schemas import Event, Scenario, Network

from .state import State

@total_ordering
class ScheduledEvent(object):
    def __init__(self, mission: Mission, event: Event):
        self.time = mission.start_date + event.mission_time
        self.event = event

    def __lt__(self, other):
        return self.time <= other.time and self.event.priority < other.event.priority

class Simulator(object):
    def execute(self, scenario: Scenario, until: bool = None) -> State:
        state = State(scenario)

        events = []
        for mission in scenario.mission_list:
            for event in mission.events:
                events.append(ScheduledEvent(mission, event))

        events = sorted(events)

        while len(events) > 0:
            event = events.pop()
            delta_t = state.time - event.time
            event.execute(state)
            # handle element demand models
