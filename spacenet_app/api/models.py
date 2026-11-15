"""
Request bodies of the application programming interface.
"""

from datetime import timedelta
from typing import List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from spacenet.schemas import AllEvents, ManifestContainerType, Scenario
from spacenet.simulation import ManifestSelection


class ScenarioRequest(CamelModel):
    """
    Request for an analysis of a scenario.
    """

    scenario: Scenario = Field(..., description="Scenario")


class StateRequest(ScenarioRequest):
    """
    Request for the simulation state before an event of a mission.
    """

    mission_index: int = Field(..., description="Position in the mission list", ge=0)
    mission_time: timedelta = Field(
        ..., description="Time relative to the start of the mission"
    )
    priority: int = Field(1, description="Priority of the event")
    exclude_event_index: Optional[int] = Field(
        None,
        description="Position of an event of the mission to leave out "
        "(e.g., the event being edited)",
        ge=0,
    )


class EvaluateRequest(ScenarioRequest):
    """
    Request to evaluate a (draft) event of a mission.
    """

    mission_index: int = Field(..., description="Position in the mission list", ge=0)
    event: AllEvents = Field(..., description="Event to evaluate")
    event_index: Optional[int] = Field(
        None,
        description="Position of the event it replaces (default: the event is added)",
        ge=0,
    )


class DemandOptions(CamelModel):
    """
    Options of a demand analysis.
    """

    estimate_container_masses: bool = Field(
        False, description="True, to add demands for packing material"
    )
    consume_existing_resources: bool = Field(
        False,
        description="True, to satisfy demands with resources available in the scenario",
    )


class DemandsRequest(ScenarioRequest):
    """
    Request for a demand analysis of a scenario.
    """

    options: DemandOptions = Field(DemandOptions(), description="Options")


class ExportRequest(DemandsRequest):
    """
    Request to export demands or a manifest as delimited text.
    """

    delimiter: str = Field(",", description="Column delimiter", pattern="^[,;\t]$")
    level: str = Field(
        "demands",
        description="Level of aggregation of a manifest export "
        "(demands, containers, carriers, or edges)",
    )


class ManifestRequest(ScenarioRequest):
    """
    Request to view or change the manifest of a scenario.
    """

    selection: Optional[ManifestSelection] = Field(
        None, description="Selection for which to report the feasible actions"
    )


class AddContainersRequest(ManifestRequest):
    """
    Request to add empty containers.
    """

    container_type: ManifestContainerType = Field(..., description="Container type")
    count: int = Field(1, description="Number of containers", ge=1, le=100)


class ContainersRequest(ManifestRequest):
    """
    Request which applies to containers (and optionally a supply edge and carrier).
    """

    container_ids: List[UUID] = Field(..., description="Container unique identifiers")
    edge_key: Optional[str] = Field(None, description="Key of the supply edge")
    carrier_id: Optional[UUID] = Field(None, description="Carrier unique identifier")


class DemandKeysRequest(ManifestRequest):
    """
    Request which applies to aggregated demands (and optionally a container).
    """

    demand_keys: List[str] = Field(..., description="Keys of the aggregated demands")
    container_id: Optional[UUID] = Field(
        None, description="Container unique identifier"
    )
