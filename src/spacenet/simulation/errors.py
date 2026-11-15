"""
Errors and warnings logged during simulation.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .elements import SimElement
    from .events import SimEvent
    from .network import SimLocation
    from .resources import DemandSet


class ScenarioError(ValueError):
    """
    An error where a simulation state could not be built from a scenario
    because, for example, an event references an unknown element.
    """

    def __init__(
        self,
        message: str,
        mission_index: Optional[int] = None,
        event_index: Optional[int] = None,
    ):
        super().__init__(message)
        #: Description of the error.
        self.message = message
        #: Position of the related mission in the scenario mission list, if any.
        self.mission_index = mission_index
        #: Position of the related event in the mission event list, if any.
        self.event_index = event_index


class SimError(Exception):
    """
    Base class for an error that occurs during simulation. Errors are raised
    by events during execution and logged by the simulator.
    """

    def __init__(self, time: float, event: Optional["SimEvent"], message: str):
        super().__init__(message)
        #: Simulation time (days) at which the error occurred.
        self.time = time
        #: Event which produced the error.
        self.event = event
        #: Description of the error.
        self.message = message

    def __str__(self):
        return f"{self.event} {self.message}"


class SimSpatialError(SimError):
    """
    An error where an event could not be executed because, for example, an
    element was not in the expected location or a capacity was exceeded.
    """


class SimDemand(SimError):
    """
    A set of demands which could not be satisfied by resources available at
    the time and location of the demand.
    """

    def __init__(
        self,
        time: float,
        event: Optional["SimEvent"],
        location: Optional["SimLocation"],
        element: Optional["SimElement"],
        demands: "DemandSet",
    ):
        demands.clean()
        super().__init__(time, event, f"Insufficient resources for demand: {demands}")
        #: Location of the demand.
        self.location = location
        #: Element which generated the demand (`None` for mission-level demands).
        self.element = element
        #: Unsatisfied demands.
        self.demands = demands


class SimWarning:
    """
    A warning about an event which does not prevent its execution.
    """

    def __init__(self, time: float, event: Optional["SimEvent"], message: str):
        #: Simulation time (days) at which the warning occurred.
        self.time = time
        #: Event which produced the warning.
        self.event = event
        #: Description of the warning.
        self.message = message

    def __str__(self):
        return f"{self.event} {self.message}"

    def __repr__(self):
        return f"SimWarning({self.time}, {str(self)!r})"
