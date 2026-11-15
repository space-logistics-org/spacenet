"""Defines object schemas for the propulsion systems and fuel tanks of vehicles."""

from enum import Enum
from typing import Any, List, Optional, Union

from fastapi_camelcase import CamelModel
from pydantic import Field, model_validator

from ..resources import GenericResourceAmount, ResourceAmount


class PropulsionType(str, Enum):
    """
    Enumeration of the types of propulsion systems (and of the burns which
    fire them).
    """

    OMS = "OMS"
    RCS = "RCS"

    def get_name(self) -> str:
        """Gets the descriptive name of this propulsion type."""
        if self == PropulsionType.OMS:
            return "Orbital Maneuvering System"
        return "Reaction Control System"


class ResourceTank(CamelModel):
    """
    Resource container for a single type of resource such as the fuel tank
    of a vehicle.
    """

    max_amount: float = Field(
        ...,
        title="Maximum Amount",
        description="Maximum resource amount (units)",
        ge=0,
    )
    contents: Union[ResourceAmount, GenericResourceAmount] = Field(
        ..., title="Contents", description="Type and amount of the contained resource"
    )


class PropulsionSystem(CamelModel):
    """
    Impulsive propulsion system with a specific impulse which burns fuel from
    its own fuel tank or from the fuel tank of another propulsion system of
    the same vehicle.
    """

    type: PropulsionType = Field(
        PropulsionType.OMS,
        title="Type",
        description="Propulsion type (fired by burns of the same type)",
    )
    isp: float = Field(
        ..., title="Specific Impulse", description="Specific impulse (s)", ge=0
    )
    fuel_tank: Optional[ResourceTank] = Field(
        None,
        title="Fuel Tank",
        description="Fuel tank (omitted if the fuel tank of another "
        "propulsion system is shared)",
    )
    shared_fuel_tank: Optional[PropulsionType] = Field(
        None,
        title="Shared Fuel Tank",
        description="Type of the propulsion system of the same vehicle whose "
        "fuel tank is shared (omitted if this system has its own fuel tank)",
    )

    @model_validator(mode="after")
    def _check_fuel_tank(self) -> "PropulsionSystem":
        if (self.fuel_tank is None) == (self.shared_fuel_tank is None):
            raise ValueError(
                "A propulsion system requires either its own fuel tank "
                "or a shared fuel tank."
            )
        if self.shared_fuel_tank == self.type:
            raise ValueError("A propulsion system cannot share its own fuel tank.")
        return self


def check_propulsion_systems(
    systems: Optional[List[PropulsionSystem]],
) -> Optional[List[PropulsionSystem]]:
    """
    Checks that the propulsion systems of a vehicle have distinct types and
    that shared fuel tanks refer to a system with its own fuel tank.

    Args:
        systems ([PropulsionSystem]): the propulsion systems of a vehicle

    Returns:
        [PropulsionSystem]: the propulsion systems
    """
    if systems is None:
        return None
    tanks = {system.type: system.fuel_tank for system in systems}
    if len(tanks) != len(systems):
        raise ValueError("Propulsion systems of a vehicle require distinct types.")
    for system in systems:
        if (
            system.shared_fuel_tank is not None
            and tanks.get(system.shared_fuel_tank) is None
        ):
            raise ValueError(
                f"The {system.type.value} propulsion system shares the fuel tank "
                f"of the {system.shared_fuel_tank.value} propulsion system "
                "which has no fuel tank."
            )
    return systems


# ---------------------------------------------------------------- legacy format

_SYSTEMS = ("propulsion_systems", "propulsionSystems")
_TANK = ("fuel_tank", "fuelTank")
_ISP = ("isp",)
_FUEL = ("fuel",)
_MAX_FUEL = ("max_fuel", "maxFuel")
_PROPULSIVE = "Propulsive Vehicle"
_SURFACE = "Surface Vehicle"


def _has(data: dict, keys) -> bool:
    return any(key in data for key in keys)


def _pop(data: dict, keys, default=None):
    value = default
    for key in keys:
        if key in data:
            found = data.pop(key)
            if found is not None:
                value = found
    return value


def _get(data, keys, default=None):
    for key in keys:
        if isinstance(data, dict):
            if data.get(key) is not None:
                return data[key]
        elif getattr(data, key, None) is not None:
            return getattr(data, key)
    return default


def _type_of(data: dict) -> Optional[str]:
    return getattr(data.get("type"), "value", data.get("type"))


def _tank(max_amount, contents) -> Optional[dict]:
    if contents is None:
        return None
    if max_amount is None:
        max_amount = _get(contents, ("amount",), 0.0)
    return {"max_amount": max_amount, "contents": contents}


def upgrade_vehicle(
    data: Any, template: Any = None, propulsive: Optional[bool] = None
) -> Any:
    """
    Converts a vehicle from the legacy format (as written by the reference
    implementation) with one specific impulse (`isp`), fuel amount (`fuel`),
    and fuel capacity (`maxFuel`) to nested propulsion systems (propulsive
    vehicles) or a nested fuel tank (surface vehicles).

    Args:
        data: the vehicle template or instantiated vehicle (converted if it
            is a dictionary in the legacy format)
        template: the template of an instantiated vehicle (dictionary or
            object schema in the current format) which provides the values
            that the instantiated vehicle does not override
        propulsive (bool): True, for a propulsive vehicle; False, for a
            surface vehicle (default: determined from the `type` field)

    Returns:
        the vehicle in the current format
    """
    if not isinstance(data, dict):
        return data
    if propulsive is None and _type_of(data) not in (_PROPULSIVE, _SURFACE):
        return data
    is_propulsive = _type_of(data) == _PROPULSIVE if propulsive is None else propulsive
    if _has(data, _SYSTEMS if is_propulsive else _TANK):
        return data
    if not _has(data, _FUEL + _MAX_FUEL + (_ISP if is_propulsive else ())):
        return data
    data = dict(data)
    fuel = _pop(data, _FUEL)
    max_fuel = _pop(data, _MAX_FUEL)
    if not is_propulsive:
        base = _get(template, _TANK)
        tank = _tank(
            (
                max_fuel
                if max_fuel is not None
                else _get(base, ("max_amount", "maxAmount"))
            ),
            fuel if fuel is not None else _get(base, ("contents",)),
        )
        if tank is not None:
            data["fuel_tank"] = tank
        return data
    isp = _pop(data, _ISP)
    systems = list(_get(template, _SYSTEMS, []))
    base = systems[0] if systems else None
    base_tank = _get(base, _TANK)
    tank = _tank(
        (
            max_fuel
            if max_fuel is not None
            else _get(base_tank, ("max_amount", "maxAmount"))
        ),
        fuel if fuel is not None else _get(base_tank, ("contents",)),
    )
    if tank is not None:
        system = {
            "type": _get(base, ("type",), PropulsionType.OMS),
            "isp": isp if isp is not None else _get(base, ("isp",), 0.0),
            "fuel_tank": tank,
        }
        data["propulsion_systems"] = [system] + systems[1:]
    return data


def upgrade_vehicles(data: Any) -> Any:
    """
    Converts the vehicles of a scenario from the legacy format (see
    :func:`upgrade_vehicle`).

    Args:
        data: the scenario (converted if it is a dictionary)

    Returns:
        the scenario with vehicles in the current format
    """
    if not isinstance(data, dict):
        return data
    templates_key = next(
        (k for k in ("element_templates", "elementTemplates") if k in data), None
    )
    instances_key = next(
        (k for k in ("instantiated_elements", "instantiatedElements") if k in data),
        None,
    )
    if templates_key is None and instances_key is None:
        return data
    data = dict(data)
    templates = {}
    if isinstance(data.get(templates_key), list):
        data[templates_key] = [upgrade_vehicle(t) for t in data[templates_key]]
        for template in data[templates_key]:
            templates[str(_get(template, ("id",)))] = template
    if isinstance(data.get(instances_key), list):
        data[instances_key] = [
            upgrade_vehicle(
                e, templates.get(str(_get(e, ("template_id", "templateId"))))
            )
            for e in data[instances_key]
        ]
    return data
