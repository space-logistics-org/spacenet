"""
Endpoints which describe the object schemas.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

import spacenet
from spacenet import schemas as s
from spacenet.schemas.demand_models import DemandModelType
from spacenet.schemas.elements.element import ElementType
from spacenet.schemas.events.event import EventType
from spacenet.schemas.scenarios.scenario import ItemDiscretizationType, ScenarioType

router = APIRouter()

#: Bodies with nodes shown for each scenario type.
SCENARIO_BODIES = {
    ScenarioType.EARTH: [s.Body.EARTH],
    ScenarioType.LUNAR: [s.Body.EARTH, s.Body.MOON],
    ScenarioType.MOON_ONLY: [s.Body.MOON],
    ScenarioType.MARTIAN: [s.Body.EARTH, s.Body.MARS],
    ScenarioType.MARS_ONLY: [s.Body.MARS],
    ScenarioType.SOLAR_SYSTEM: list(s.Body),
}


def _values(enumeration) -> list:
    return [member.value for member in enumeration]


@router.get("/schema")
def get_schema() -> dict:
    """
    Gets the JSON schema of a scenario.
    """
    return s.Scenario.model_json_schema(by_alias=True)


@router.get("/enums")
def get_enumerations() -> dict:
    """
    Gets the values of the enumerations used by scenarios.
    """
    classes = list(s.ClassOfSupply)
    return {
        "version": spacenet.__version__,
        "classesOfSupply": [
            {
                "id": int(c),
                "name": c.get_name(),
                "base": None if c.get_base_class() is None else int(c.get_base_class()),
            }
            for c in classes
        ],
        "environments": _values(s.Environment),
        "bodies": _values(s.Body),
        "nodeTypes": _values(s.NodeType),
        "edgeTypes": _values(s.EdgeType),
        "elementTypes": _values(ElementType),
        "propulsionTypes": [
            {"id": t.value, "name": t.get_name()} for t in s.PropulsionType
        ],
        "eventTypes": _values(EventType),
        "stateTypes": _values(s.StateType),
        "resourceTypes": _values(s.ResourceType),
        "demandModelTypes": _values(DemandModelType),
        "itemDiscretization": _values(ItemDiscretizationType),
        "containerTypes": [
            t.value
            for t in s.ManifestContainerType
            if t != s.ManifestContainerType.CUSTOM
        ],
        "scenarioTypes": [
            {"name": t.value, "bodies": _values(SCENARIO_BODIES[t])}
            for t in ScenarioType
        ],
    }


@router.get("/defaults", response_model_by_alias=True)
def get_defaults() -> s.Scenario:
    """
    Gets a new (empty) scenario with the default configuration.
    """
    today = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return s.Scenario(
        name="New Scenario",
        created_by="",
        start_date=today,
        scenario_type=ScenarioType.LUNAR,
    )
