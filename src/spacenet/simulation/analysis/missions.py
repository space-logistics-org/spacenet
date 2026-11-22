"""
Object schemas for the validation of missions and their events.
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ...schemas import Scenario
from ..events import EvaEvent, ExplorationProcess, SimEvent, TransportEvent
from ..simulator import MiniSimulator
from .issues import KIND_WARNING, IssueReference, SimIssue, collect_issues


def _finite(value: Optional[float]) -> Optional[float]:
    return value if value is not None and abs(value) != float("inf") else None


class EventSummary(CamelModel):
    """
    Summary of an event of a mission.
    """

    index: int = Field(..., description="Position in the mission event list")
    name: str = Field(..., description="Event name")
    type: Optional[str] = Field(None, description="Event type")
    time: float = Field(..., description="Time (days) relative to the scenario start")
    mission_time: float = Field(
        ..., description="Time (days) relative to the mission start"
    )
    priority: int = Field(..., description="Priority")
    location: Optional[UUID] = Field(None, description="Location unique identifier")
    duration: Optional[float] = Field(
        None, description="Duration (days) of a transport, exploration, or EVA"
    )
    origin: Optional[UUID] = Field(
        None, description="Origin node unique identifier of a transport"
    )
    destination: Optional[UUID] = Field(
        None, description="Destination node unique identifier of a transport"
    )
    errors: List[str] = Field([], description="Errors produced by the event")
    warnings: List[str] = Field([], description="Warnings produced by the event")

    @classmethod
    def create(cls, event: SimEvent, start_time: float, settings) -> "EventSummary":
        """Creates the summary of an event of a mission starting at a time."""
        mission_time = settings.round_time(event.mission_time or 0.0)
        summary = cls(
            index=event.event_index,
            name=event.name,
            type=None if event.event_type is None else event.event_type.value,
            time=start_time + mission_time,
            mission_time=mission_time,
            priority=event.priority,
            location=None if event.location is None else event.location.id,
        )
        if isinstance(event, TransportEvent):
            summary.duration = _finite(event.duration)
            if event.edge is not None:
                summary.origin = event.origin.id
                summary.destination = event.destination.id
        elif isinstance(event, ExplorationProcess):
            summary.duration = event.duration
        elif isinstance(event, EvaEvent):
            summary.duration = event.eva_duration / 24
        return summary


class MissionSummary(CamelModel):
    """
    Summary of a mission.
    """

    index: int = Field(..., description="Position in the scenario mission list")
    name: str = Field(..., description="Mission name")
    start_time: float = Field(
        ..., description="Start time (days) relative to the scenario start"
    )
    duration: float = Field(0.0, description="Duration (days)")
    crew_size: int = Field(0, description="Number of crew members created")
    error_count: int = Field(0, description="Number of errors")
    warning_count: int = Field(0, description="Number of warnings")
    events: List[EventSummary] = Field([], description="Events")


class LocationSegment(CamelModel):
    """
    Period of time during which an element is at one location.
    """

    start_time: float = Field(..., description="Start time (days)")
    end_time: float = Field(..., description="End time (days)")
    location: UUID = Field(..., description="Location unique identifier")


class ElementLocationHistory(CamelModel):
    """
    Locations of an element over time.
    """

    element: IssueReference = Field(..., description="Element")
    type: Optional[str] = Field(None, description="Element type")
    segments: List[LocationSegment] = Field([], description="Periods at one location")


class LocationSummary(CamelModel):
    """
    Summary of a network location.
    """

    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    is_edge: bool = Field(False, description="True, if the location is an edge")


class MissionsAnalysis(CamelModel):
    """
    Validation of the missions of a scenario: the errors and warnings of
    each event and the location of each element over time.
    """

    issues: List[SimIssue] = Field([], description="Errors and warnings")
    missions: List[MissionSummary] = Field([], description="Missions")
    element_history: List[ElementLocationHistory] = Field(
        [], description="Locations of each element over time"
    )
    locations: List[LocationSummary] = Field([], description="Network locations")
    end_time: float = Field(
        0.0,
        description="Time (days) of the scenario end (default: the last event)",
    )

    @classmethod
    def create(cls, scenario: Scenario) -> "MissionsAnalysis":
        """
        Simulates the events of a scenario (without satisfying demands) to
        validate its missions.

        Args:
            scenario (:obj:`Scenario`): The scenario.

        Returns:
            :obj:`MissionsAnalysis`: The analysis results.
        """
        simulator = MiniSimulator(scenario)
        simulator.simulate()
        issues = collect_issues(simulator, demands=False)
        settings = simulator.settings
        missions = []
        for mission in simulator.state.missions:
            summary = MissionSummary(
                index=mission.index,
                name=mission.name,
                start_time=mission.start_time,
                duration=_finite(mission.duration) or 0.0,
                crew_size=mission.crew_size,
                events=[
                    EventSummary.create(e, mission.start_time, settings)
                    for e in mission.events
                ],
            )
            for issue in issues:
                if issue.mission_index != mission.index:
                    continue
                is_warning = issue.kind == KIND_WARNING
                if is_warning:
                    summary.warning_count += 1
                else:
                    summary.error_count += 1
                if issue.event_index is not None:
                    event = summary.events[issue.event_index]
                    (event.warnings if is_warning else event.errors).append(
                        issue.message
                    )
            missions.append(summary)
        return cls(
            issues=issues,
            missions=missions,
            element_history=cls._get_element_history(simulator),
            locations=[
                LocationSummary(id=n.id, name=n.name)
                for n in simulator.state.network.nodes
            ]
            + [
                LocationSummary(id=e.id, name=e.name, is_edge=True)
                for e in simulator.state.network.edges
            ],
            end_time=simulator.time,
        )

    @staticmethod
    def _get_element_history(simulator: MiniSimulator) -> List[ElementLocationHistory]:
        histories: Dict[UUID, ElementLocationHistory] = {}
        current: Dict[UUID, LocationSegment] = {}
        for snapshot in simulator.location_history:
            present = set()
            for element in snapshot.elements:
                location = snapshot.get_location(element)
                if location is None:
                    continue
                present.add(element.id)
                if element.id not in histories:
                    histories[element.id] = ElementLocationHistory(
                        element=IssueReference(id=element.id, name=element.name),
                        type=(
                            None
                            if element.element_type is None
                            else element.element_type.value
                        ),
                    )
                segment = current.get(element.id)
                if segment is not None and segment.location == location.id:
                    segment.end_time = snapshot.time
                else:
                    if segment is not None:
                        segment.end_time = snapshot.time
                    segment = LocationSegment(
                        start_time=snapshot.time,
                        end_time=snapshot.time,
                        location=location.id,
                    )
                    current[element.id] = segment
                    histories[element.id].segments.append(segment)
            for element_id in [i for i in current if i not in present]:
                current.pop(element_id).end_time = snapshot.time
        return sorted(histories.values(), key=lambda h: h.element.name)
