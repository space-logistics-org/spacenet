"""
Writes scenarios in the JSON format read by the reference (Java)
implementation, which predates some fields of the object schemas.
"""

import json
from typing import Any, Dict

from spacenet import schemas as s


class UnsupportedError(ValueError):
    """A scenario uses a feature which the reference implementation lacks."""


def _vehicle(element: Dict[str, Any]):
    """Converts nested propulsion systems to a single specific impulse and fuel tank."""
    systems = element.pop("propulsionSystems", None)
    if systems is None:
        return
    if len(systems) != 1 or systems[0].get("type", "OMS") != "OMS":
        raise UnsupportedError(f"{element['name']}: only one OMS system is supported")
    system = systems[0]
    if system.get("oxidizerTank") or system.get("sharedOxidizerTank"):
        raise UnsupportedError(
            f"{element['name']}: bipropellant systems are unsupported"
        )
    tank = system["fuelTank"]
    if tank.get("boiloffRate"):
        raise UnsupportedError(f"{element['name']}: boiloff is unsupported")
    element["isp"] = system["isp"]
    element["fuel"] = tank["contents"]
    element["maxFuel"] = tank["maxAmount"]


def _event(event: Dict[str, Any], types: Dict[str, str]):
    """
    Adds the fields of events which the reference implementation names
    differently (keeping the fields of the object schemas, which the
    reference implementation ignores, so that both can read the file).
    """
    kind = event["type"]
    if kind == "Propulsive Burn":
        event["actions"] = event["burnStageSequence"]
    elif kind == "Transfer Resources":
        if event.get("transferMode") not in (None, "Amount") or event.get(
            "lossFraction"
        ):
            raise UnsupportedError(f"{event['name']}: transfer options are unsupported")
        if event.get("originTank") or event.get("destinationTank"):
            raise UnsupportedError(f"{event['name']}: tank selectors are unsupported")
        for field in ("originContainer", "destinationContainer"):
            if types.get(event[field]) != "Resource Container":
                raise UnsupportedError(
                    f"{event['name']}: transfers require resource containers"
                )
        event["origin"] = event["originContainer"]
        event["destination"] = event["destinationContainer"]
    elif kind == "Reconfigure Element" and event["stateIndex"] < 0:
        raise UnsupportedError(f"{event['name']}: a state index of -1 is unsupported")
    elif kind == "Crewed EVA":
        event["elements"] = [state["element"] for state in event["elementStates"]]
    elif kind == "Surface Transport":
        raise UnsupportedError("surface transports use other units (see the tests)")


def to_legacy(scenario: s.Scenario) -> Dict[str, Any]:
    """
    Converts a scenario to a JSON representation which both the reference
    implementation and the object schemas read.

    Args:
        scenario (:obj:`Scenario`): The scenario.

    Returns:
        dict: The JSON representation.

    Raises:
        :obj:`UnsupportedError`: If the scenario uses a feature which the
            reference implementation lacks.
    """
    if scenario.end_date is not None:
        raise UnsupportedError("the scenario end date is unsupported")
    configuration = scenario.configuration
    if configuration.time_phased_consumables or configuration.part_failures:
        raise UnsupportedError(
            "time-phased consumables and part failures are unsupported"
        )
    if configuration.max_time_step is not None:
        raise UnsupportedError("the maximum time step is unsupported")
    data = scenario.model_dump(mode="json", by_alias=True, exclude_none=True)
    for element in [*data["elementTemplates"], *data["instantiatedElements"]]:
        if element["type"] == "Propulsive Vehicle":
            _vehicle(element)
        if element.get("energyStorage") or element.get("unitCost") is not None:
            raise UnsupportedError(f"{element['name']}: power and cost are unsupported")
    types = {e["id"]: e["type"] for e in data["instantiatedElements"]}
    for mission in data["missionList"]:
        for event in mission["events"]:
            _event(event, types)
    return data


def write_legacy(scenario: s.Scenario, path):
    """Writes a scenario in the JSON format of the reference implementation."""
    with open(path, "w", encoding="utf-8", newline="\n") as file:
        json.dump(to_legacy(scenario), file, indent=2)
        file.write("\n")
