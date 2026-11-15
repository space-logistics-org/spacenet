"""
Object schemas for errors and warnings logged by a simulator.
"""

from typing import List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..errors import ScenarioError, SimDemand, SimError, SimWarning
from ..simulator import Simulator

#: Issue kind for an event which could not be executed.
KIND_SPATIAL = "spatial"
#: Issue kind for demands which could not be satisfied.
KIND_DEMAND = "demand"
#: Issue kind for a warning which does not prevent execution.
KIND_WARNING = "warning"
#: Issue kind for a scenario from which no simulation state could be built.
KIND_SCENARIO = "scenario"


class IssueReference(CamelModel):
    """
    Reference to a location or an element.
    """

    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")

    @classmethod
    def create(cls, source) -> Optional["IssueReference"]:
        """Creates a reference to a location or an element."""
        if source is None:
            return None
        return cls(id=source.id, name=source.name)


class SimIssue(CamelModel):
    """
    An error or a warning logged by a simulator, related (where known) to
    the scenario event which produced it.
    """

    kind: str = Field(
        ..., description="Kind of issue (spatial, demand, warning, or scenario)"
    )
    time: float = Field(0.0, description="Time (days) relative to the scenario start")
    message: str = Field(..., description="Description of the issue")
    event_name: Optional[str] = Field(
        None, description="Name of the simulation event which produced the issue"
    )
    mission_index: Optional[int] = Field(
        None, description="Position of the related mission in the mission list"
    )
    event_index: Optional[int] = Field(
        None, description="Position of the related event in the mission event list"
    )
    location: Optional[IssueReference] = Field(None, description="Related location")
    element: Optional[IssueReference] = Field(None, description="Related element")

    @classmethod
    def from_error(cls, error: SimError) -> "SimIssue":
        """
        Creates an issue from a simulation error.

        Args:
            error (:obj:`SimError`): The error.

        Returns:
            :obj:`SimIssue`: The issue.
        """
        event = error.event
        mission_index, event_index = (None, None) if event is None else event.source
        is_demand = isinstance(error, SimDemand)
        return cls(
            kind=KIND_DEMAND if is_demand else KIND_SPATIAL,
            time=error.time,
            message=error.message,
            event_name=None if event is None else event.name,
            mission_index=mission_index,
            event_index=event_index,
            location=IssueReference.create(
                error.location if is_demand else getattr(event, "location", None)
            ),
            element=IssueReference.create(error.element) if is_demand else None,
        )

    @classmethod
    def from_warning(cls, warning: SimWarning) -> "SimIssue":
        """
        Creates an issue from a simulation warning.

        Args:
            warning (:obj:`SimWarning`): The warning.

        Returns:
            :obj:`SimIssue`: The issue.
        """
        event = warning.event
        mission_index, event_index = (None, None) if event is None else event.source
        return cls(
            kind=KIND_WARNING,
            time=warning.time,
            message=warning.message,
            event_name=None if event is None else event.name,
            mission_index=mission_index,
            event_index=event_index,
            location=IssueReference.create(getattr(event, "location", None)),
        )

    @classmethod
    def from_scenario_error(cls, error: ScenarioError) -> "SimIssue":
        """
        Creates an issue from an error building a simulation state.

        Args:
            error (:obj:`ScenarioError`): The error.

        Returns:
            :obj:`SimIssue`: The issue.
        """
        return cls(
            kind=KIND_SCENARIO,
            message=error.message,
            mission_index=error.mission_index,
            event_index=error.event_index,
        )


def collect_issues(
    simulator: Simulator, *, demands: bool = True, warnings: bool = True
) -> List[SimIssue]:
    """
    Collects the errors and warnings logged by an executed simulator.

    Args:
        simulator (:obj:`Simulator`): The simulator.
        demands (bool): True, to include unsatisfied demands.
        warnings (bool): True, to include warnings.

    Returns:
        :obj:`List[SimIssue]`: The issues in order of time.
    """
    issues = [SimIssue.from_error(e) for e in simulator.spatial_errors]
    if demands:
        issues.extend(SimIssue.from_error(e) for e in simulator.unsatisfied_demands)
    if warnings:
        issues.extend(SimIssue.from_warning(w) for w in simulator.warnings)
    return sorted(issues, key=lambda i: i.time)
