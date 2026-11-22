"""
Checks a scenario for problems which prevent or invalidate its simulation
(errors) or which are likely to be mistakes (warnings), reporting all of them
at once rather than the first one encountered.

Each issue identifies the field of the scenario with a path in its JSON
representation (as used by trade studies), e.g. ``missionList/0/events/2``.

Usage: ``python -m spacenet.lint scenario.json [...]`` prints the issues of
each scenario and exits with status 1 if any scenario has errors.
"""

import argparse
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field, ValidationError

from . import schemas as s
from .schemas.elements.element import ElementType
from .schemas.events.event import EventType

__all__ = ["Severity", "LintIssue", "lint_scenario", "errors", "main"]


class Severity(str, Enum):
    """Enumeration of the severities of scenario issues."""

    #: The scenario cannot be simulated (or its simulation would be invalid).
    ERROR = "Error"
    #: The scenario can be simulated but is likely to contain a mistake.
    WARNING = "Warning"


class LintIssue(CamelModel):
    """A problem found in a scenario."""

    severity: Severity = Field(..., description="Severity")
    code: str = Field(..., description="Identifier of the kind of issue")
    message: str = Field(..., description="Description of the issue")
    path: str = Field(
        ..., description="Path of the field in the JSON representation of the scenario"
    )
    mission_index: Optional[int] = Field(
        None, description="Position of the related mission in the mission list"
    )
    event_index: Optional[int] = Field(
        None, description="Position of the related event in the mission event list"
    )

    def __str__(self):
        return f"{self.severity.value} [{self.code}] {self.path}: {self.message}"


#: Element types which can contain other elements.
CARRIER_TYPES = (
    ElementType.ELEMENT_CARRIER,
    ElementType.PROPULSIVE_VEHICLE,
    ElementType.SURFACE_VEHICLE,
)

#: Event types which add resources, for which amounts must not be negative.
_SUPPLY_EVENTS = (EventType.ADD_RESOURCES, EventType.TRANSFER_RESOURCES)


def _value(enum_or_value) -> str:
    return getattr(enum_or_value, "value", enum_or_value)


def _utc(date: datetime) -> datetime:
    return date if date.tzinfo is not None else date.replace(tzinfo=timezone.utc)


class _Linter:
    """Accumulates the issues of one scenario."""

    # pylint: disable=too-many-instance-attributes,too-many-public-methods

    def __init__(self, scenario: s.Scenario):
        self.scenario = scenario
        self.issues: List[LintIssue] = []
        network = scenario.network
        self.nodes = {n.id: n for n in network.nodes}
        self.edges = {e.id: e for e in network.edges}
        self.templates = {t.id: t for t in scenario.element_templates}
        self.instances = {e.id: e for e in scenario.instantiated_elements}
        self.resources = {r.id: r for r in scenario.resource_list}
        self.demand_models = {m.id: m for m in scenario.demand_models}
        self.burns = {b.id: e for e in network.edges for b in getattr(e, "burns", [])}
        self._mission: Optional[int] = None
        self._event: Optional[int] = None

    # ------------------------------------------------------------- reporting

    def _add(self, severity: Severity, code: str, path: str, message: str):
        self.issues.append(
            LintIssue(
                severity=severity,
                code=code,
                message=message,
                path=path,
                mission_index=self._mission,
                event_index=self._event,
            )
        )

    def error(self, code: str, path: str, message: str):
        """Reports an error."""
        self._add(Severity.ERROR, code, path, message)

    def warning(self, code: str, path: str, message: str):
        """Reports a warning."""
        self._add(Severity.WARNING, code, path, message)

    # --------------------------------------------------------------- lookups

    def element_type(self, element_id: UUID) -> Optional[ElementType]:
        """Gets the type of an instantiated element (None if unknown)."""
        element = self.instances.get(element_id)
        return None if element is None else ElementType(element.type)

    def effective(self, element, name: str, default=None):
        """Gets an attribute of an element instance or else of its template."""
        result = getattr(element, name, None)
        if result is None and hasattr(element, "template_id"):
            template = self.templates.get(element.template_id)
            result = getattr(template, name, None)
        return default if result is None else result

    def name_of(self, element_id: UUID) -> str:
        """Gets a descriptive name of an element (or its identifier)."""
        element = self.instances.get(element_id) or self.templates.get(element_id)
        return str(element_id) if element is None else element.name

    # ---------------------------------------------------------------- checks

    def run(self) -> List[LintIssue]:
        """Checks the scenario and returns its issues."""
        self.check_identifiers()
        self.check_network()
        self.check_resources()
        self.check_demand_models()
        for index, template in enumerate(self.scenario.element_templates):
            self.check_element(template, f"elementTemplates/{index}")
        for index, element in enumerate(self.scenario.instantiated_elements):
            self.check_instance(element, f"instantiatedElements/{index}")
        self.check_initial_containment()
        for index, mission in enumerate(self.scenario.mission_list):
            self._mission = index
            self.check_mission(mission, f"missionList/{index}")
        self._mission = None
        self.check_creations()
        return self.issues

    def check_identifiers(self):
        """Checks that unique identifiers are unique."""
        # pylint: disable=too-many-locals
        collections = [
            ("network/nodes", self.scenario.network.nodes, "location"),
            ("network/edges", self.scenario.network.edges, "location"),
            ("instantiatedElements", self.scenario.instantiated_elements, "element"),
            ("elementTemplates", self.scenario.element_templates, "template"),
            ("resourceList", self.scenario.resource_list, "resource"),
            ("demandModels", self.scenario.demand_models, "demand model"),
        ]
        seen: Dict[UUID, List[tuple]] = defaultdict(list)
        for path, items, kind in collections:
            for index, item in enumerate(items):
                for previous_path, previous_kind, previous_name in seen[item.id]:
                    # identifiers are looked up within each kind, except that
                    # containers are looked up among locations and elements
                    if kind != previous_kind and {kind, previous_kind} != {
                        "location",
                        "element",
                    }:
                        continue
                    self.error(
                        "duplicate-id",
                        f"{path}/{index}",
                        f"The {kind} {item.name} has the same identifier as the "
                        f"{previous_kind} {previous_name} ({previous_path}).",
                    )
                    break
                seen[item.id].append((f"{path}/{index}", kind, item.name))
        burns: Dict[UUID, str] = {}
        for edge_index, edge in enumerate(self.scenario.network.edges):
            for burn_index, burn in enumerate(getattr(edge, "burns", [])):
                path = f"network/edges/{edge_index}/burns/{burn_index}"
                if burn.id in burns:
                    self.error(
                        "duplicate-id",
                        path,
                        f"A burn of {edge.name} has the same identifier as the "
                        f"burn {burns[burn.id]}.",
                    )
                burns[burn.id] = path

    def check_network(self):
        """Checks the edges and the initial contents of locations."""
        for index, edge in enumerate(self.scenario.network.edges):
            path = f"network/edges/{index}"
            for field in ("origin", "destination"):
                if getattr(edge, field) not in self.nodes:
                    self.error(
                        "unknown-node",
                        f"{path}/{field}",
                        f"The {field} of {edge.name} is not a node of the network.",
                    )
            if edge.origin == edge.destination:
                self.warning(
                    "loop-edge",
                    path,
                    f"{edge.name} has the same origin and destination.",
                )
            duration = getattr(edge, "duration", None)
            for burn_index, burn in enumerate(getattr(edge, "burns", [])):
                burn_path = f"{path}/burns/{burn_index}/time"
                if burn.time < timedelta(0):
                    self.error(
                        "negative-time",
                        burn_path,
                        f"A burn of {edge.name} is before the start of the transport.",
                    )
                elif duration is not None and burn.time > duration:
                    self.warning(
                        "burn-after-arrival",
                        burn_path,
                        f"A burn of {edge.name} is after the end of the transport.",
                    )
        for kind, locations in (
            ("nodes", self.scenario.network.nodes),
            ("edges", self.scenario.network.edges),
        ):
            for index, location in enumerate(locations):
                for item_index, item in enumerate(location.contents):
                    if item.id not in self.instances:
                        self.error(
                            "unknown-element",
                            f"network/{kind}/{index}/contents/{item_index}",
                            f"{location.name} contains an unknown element {item.id}.",
                        )

    def check_resources(self):
        """Checks the resource list."""
        names = defaultdict(list)
        for index, resource in enumerate(self.scenario.resource_list):
            names[resource.name].append(index)
        for name, indices in names.items():
            if len(indices) > 1:
                self.warning(
                    "duplicate-name",
                    f"resourceList/{indices[1]}",
                    f"{len(indices)} resources are named {name}.",
                )

    def check_amounts(
        self,
        amounts: Optional[Iterable],
        path: str,
        owner: str,
        *,
        non_negative: bool = False,
    ):
        """Checks that resource amounts (or rates) reference known resources."""
        for index, amount in enumerate(amounts or []):
            self.check_amount(
                amount, f"{path}/{index}", owner, non_negative=non_negative
            )

    def check_amount(self, amount, path: str, owner: str, *, non_negative=False):
        """Checks that a resource amount (or rate) references a known resource."""
        resource = getattr(amount, "resource", None)
        if resource is not None and resource not in self.resources:
            self.error(
                "unknown-resource",
                f"{path}/resource",
                f"{owner} references an unknown resource {resource}.",
            )
        quantity = getattr(amount, "amount", None)
        if non_negative and quantity is not None and quantity < 0:
            self.error(
                "negative-amount",
                f"{path}/amount",
                f"{owner} has a negative amount ({quantity:g}) of a resource.",
            )

    def unit_mass(self, amount) -> float:
        """Gets the mass (kg) of one unit of the resource of an amount."""
        resource = self.resources.get(getattr(amount, "resource", None))
        return 1.0 if resource is None else resource.unit_mass

    def check_demand_models(self):
        """Checks the demand model templates."""
        for index, model in enumerate(self.scenario.demand_models):
            path = f"demandModels/{index}"
            owner = f"Demand model {model.name}"
            for field in ("demands", "inputs", "outputs"):
                self.check_amounts(
                    getattr(model, field, None), f"{path}/{field}", owner
                )

    def check_model_instance(self, model, path: str, owner: str):
        """
        Checks an instantiated demand model of an element or a mission (the
        object schemas restrict the types of demand models of each).
        """
        template = self.demand_models.get(model.template_id)
        model_type = s.DemandModelType(model.type)
        if template is None:
            self.error(
                "unknown-demand-model",
                f"{path}/templateId",
                f"{owner} references an unknown demand model {model.template_id}.",
            )
        elif s.DemandModelType(template.type) != model_type:
            self.error(
                "demand-model-type-mismatch",
                f"{path}/type",
                f"{owner} has a {model_type.value} demand model which instantiates "
                f"the {_value(template.type)} demand model {template.name}.",
            )
        for field in ("demands", "inputs", "outputs"):
            self.check_amounts(getattr(model, field, None), f"{path}/{field}", owner)

    def check_tank(self, tank: Optional[s.ResourceTank], path: str, owner: str):
        """Checks a resource tank of a vehicle."""
        if tank is None:
            return
        self.check_amount(tank.contents, f"{path}/contents", owner, non_negative=True)
        if tank.contents.amount > tank.max_amount * (1 + 1e-9):
            self.warning(
                "over-capacity",
                f"{path}/contents/amount",
                f"{owner} holds {tank.contents.amount:,g} units in a tank with a "
                f"capacity of {tank.max_amount:,g} units.",
            )

    def check_element(self, element, path: str):
        """
        Checks the attributes of an element template or the attributes which
        an element instance defines (others are checked with its template).
        """
        owner = f"Element {element.name}"
        for index, part in enumerate(getattr(element, "parts", None) or []):
            if part.resource not in self.resources:
                self.error(
                    "unknown-resource",
                    f"{path}/parts/{index}/resource",
                    f"{owner} has a part of an unknown resource {part.resource}.",
                )
        for index, state in enumerate(getattr(element, "states", None) or []):
            for model_index, model in enumerate(state.demand_models):
                self.check_model_instance(
                    model,
                    f"{path}/states/{index}/demandModels/{model_index}",
                    owner,
                )
        element_type = ElementType(element.type)
        if element_type == ElementType.RESOURCE_CONTAINER:
            contents = getattr(element, "contents", None)
            self.check_amounts(contents, f"{path}/contents", owner, non_negative=True)
        for index, system in enumerate(
            getattr(element, "propulsion_systems", None) or []
        ):
            system_path = f"{path}/propulsionSystems/{index}"
            self.check_tank(system.fuel_tank, f"{system_path}/fuelTank", owner)
            self.check_tank(system.oxidizer_tank, f"{system_path}/oxidizerTank", owner)
        if element_type == ElementType.SURFACE_VEHICLE:
            self.check_tank(
                getattr(element, "fuel_tank", None), f"{path}/fuelTank", owner
            )
        if element_type in CARRIER_TYPES:
            for index, item in enumerate(getattr(element, "contents", None) or []):
                item_id = getattr(item, "id", item)
                if item_id not in self.instances and item_id not in self.templates:
                    self.error(
                        "unknown-element",
                        f"{path}/contents/{index}",
                        f"{owner} contains an unknown element {item_id}.",
                    )

    def check_instance(self, element, path: str):
        """Checks an element instance."""
        owner = f"Element {element.name}"
        template = self.templates.get(element.template_id)
        if template is None:
            self.error(
                "unknown-template",
                f"{path}/templateId",
                f"{owner} instantiates an unknown element template "
                f"{element.template_id}.",
            )
        elif ElementType(template.type) != ElementType(element.type):
            self.warning(
                "template-type-mismatch",
                f"{path}/type",
                f"{owner} is a {_value(element.type)} which instantiates the "
                f"{_value(template.type)} template {template.name}.",
            )
        self.check_element(element, path)
        states = self.effective(element, "states", [])
        index = self.effective(element, "current_state_index")
        if index is not None and index >= len(states):
            self.error(
                "invalid-state-index",
                f"{path}/currentStateIndex",
                f"{owner} has {len(states)} states but a current state index of "
                f"{index}.",
            )
        if ElementType(element.type) == ElementType.RESOURCE_CONTAINER:
            self.check_container_capacity(element, path, owner)

    def check_container_capacity(self, element, path: str, owner: str):
        """Checks that the initial contents of a resource container fit."""
        capacity = self.effective(element, "max_cargo_mass", 0.0)
        contents = self.effective(element, "contents", [])
        mass = sum(a.amount * self.unit_mass(a) for a in contents)
        if capacity and mass > capacity * (1 + 1e-9):
            self.warning(
                "over-capacity",
                f"{path}/contents",
                f"{owner} initially holds {mass:,.1f} kg of resources but has a "
                f"cargo capacity of {capacity:,.1f} kg.",
            )

    def check_initial_containment(self):
        """
        Checks that each element is initially in at most one carrier or
        location and that no carrier (recursively) contains itself.
        """
        # pylint: disable=too-many-locals,too-many-branches
        holders: Dict[UUID, List[str]] = defaultdict(list)
        children: Dict[UUID, List[UUID]] = defaultdict(list)
        paths: Dict[UUID, str] = {}
        for kind, locations in (
            ("nodes", self.scenario.network.nodes),
            ("edges", self.scenario.network.edges),
        ):
            for index, location in enumerate(locations):
                for item_index, item in enumerate(location.contents):
                    holders[item.id].append(location.name)
                    paths.setdefault(
                        item.id, f"network/{kind}/{index}/contents/{item_index}"
                    )
        for index, element in enumerate(self.scenario.instantiated_elements):
            if ElementType(element.type) not in CARRIER_TYPES:
                continue
            for item_index, item in enumerate(self.effective(element, "contents", [])):
                item_id = getattr(item, "id", item)
                if item_id not in self.instances:
                    continue  # templates are instantiated for each carrier
                holders[item_id].append(element.name)
                children[element.id].append(item_id)
                paths.setdefault(
                    item_id, f"instantiatedElements/{index}/contents/{item_index}"
                )
        for element_id, names in holders.items():
            if len(names) > 1 and element_id in self.instances:
                self.error(
                    "multiple-containers",
                    paths[element_id],
                    f"Element {self.name_of(element_id)} is initially inside "
                    f"{len(names)} containers ({', '.join(names)}).",
                )
        reported = set()
        for index, element in enumerate(self.scenario.instantiated_elements):
            stack, seen = list(children.get(element.id, [])), set()
            while stack:
                child = stack.pop()
                if child == element.id:
                    cycle = frozenset(seen | {element.id})
                    if cycle not in reported:
                        reported.add(cycle)
                        self.error(
                            "containment-cycle",
                            f"instantiatedElements/{index}/contents",
                            f"Element {element.name} contains itself.",
                        )
                    break
                if child in seen:
                    continue
                seen.add(child)
                stack.extend(children.get(child, []))

    # -------------------------------------------------------------- missions

    def check_mission(self, mission: s.Mission, path: str):
        """Checks a mission and its events."""
        owner = f"Mission {mission.name}"
        for field in ("origin", "destination", "return_origin", "return_destination"):
            node = getattr(mission, field)
            if node is not None and node not in self.nodes:
                camel = "".join(
                    part if i == 0 else part.title()
                    for i, part in enumerate(field.split("_"))
                )
                self.error(
                    "unknown-node",
                    f"{path}/{camel}",
                    f"The {field.replace('_', ' ')} of {owner} is not a node of "
                    "the network.",
                )
        start = _utc(mission.start_date)
        if start < _utc(self.scenario.start_date):
            self.error(
                "before-scenario-start",
                f"{path}/startDate",
                f"{owner} starts before the scenario start date.",
            )
        # events after the scenario end date are reported by the simulators
        for index, model in enumerate(mission.demand_models):
            self.check_model_instance(
                model,
                f"{path}/demandModels/{index}",
                owner,
            )
        for index, event in enumerate(mission.events):
            self._event = index
            self.check_event(event, f"{path}/events/{index}")
        self._event = None

    def require_location(self, location_id: UUID, path: str, owner: str) -> bool:
        """Checks that a location exists."""
        if location_id in self.nodes or location_id in self.edges:
            return True
        self.error(
            "unknown-location",
            path,
            f"{owner} references an unknown location {location_id}.",
        )
        return False

    def require_element(
        self,
        element_id: UUID,
        path: str,
        owner: str,
        types: Sequence[ElementType] = (),
        role: str = "",
    ) -> bool:
        """Checks that an element exists (and has one of a set of types)."""
        element_type = self.element_type(element_id)
        if element_type is None:
            self.error(
                "unknown-element",
                path,
                f"{owner} references an unknown element {element_id}.",
            )
            return False
        if types and element_type not in types:
            self.error(
                "wrong-element-type",
                path,
                f"{owner} requires {role}, but {self.name_of(element_id)} is a "
                f"{element_type.value}.",
            )
            return False
        return True

    def require_elements(self, element_ids, path: str, owner: str):
        """Checks that elements exist."""
        for index, element_id in enumerate(element_ids):
            self.require_element(element_id, f"{path}/{index}", owner)

    def require_state(self, element_id: UUID, index: Optional[int], path, owner):
        """Checks that a state index is valid for an element."""
        element = self.instances.get(element_id)
        if element is None or index is None or index < 0:
            return
        states = self.effective(element, "states", [])
        if index >= len(states):
            self.error(
                "invalid-state-index",
                path,
                f"{owner} selects state {index} of {element.name}, which has "
                f"{len(states)} states.",
            )

    def require_edge(self, edge_id: UUID, edge_type: s.EdgeType, path, owner):
        """Checks that an edge exists and has a type; returns it if so."""
        edge = self.edges.get(edge_id)
        if edge is None:
            self.error(
                "unknown-edge", path, f"{owner} references an unknown edge {edge_id}."
            )
            return None
        if s.EdgeType(edge.type) != edge_type:
            self.error(
                "wrong-edge-type",
                path,
                f"{owner} requires a {edge_type.value}, but {edge.name} is a "
                f"{_value(edge.type)}.",
            )
            return None
        return edge

    def check_departure(self, event, edge, path: str, owner: str, both_ends=False):
        """Warns if a transport does not depart from an end of its edge."""
        ends = (edge.origin, edge.destination) if both_ends else (edge.origin,)
        if event.location not in ends and event.location in self.nodes:
            where = "either end" if both_ends else "the origin"
            self.warning(
                "transport-location",
                f"{path}/location",
                f"{owner} is located at {self.nodes[event.location].name}, not at "
                f"{where} of {edge.name}.",
            )

    def check_burn_items(self, items, path: str, owner: str):
        """Checks the burn and stage actions of a burn sequence."""
        for index, item in enumerate(items):
            item_path = f"{path}/{index}/element"
            if not self.require_element(item.element, item_path, owner):
                continue
            if (
                _value(item.type) == "Burn"
                and self.element_type(item.element) != ElementType.PROPULSIVE_VEHICLE
            ):
                self.warning(
                    "not-propulsive",
                    item_path,
                    f"{owner} burns {self.name_of(item.element)}, which is not a "
                    "propulsive vehicle.",
                )

    def check_event(self, event, path: str):
        """Checks an event of a mission."""
        # pylint: disable=too-many-branches,too-many-statements,too-many-locals
        owner = f"Event {event.name}"
        event_type = EventType(event.type)
        if event.mission_time < timedelta(0):
            self.error(
                "negative-time",
                f"{path}/missionTime",
                f"{owner} is before the start of its mission.",
            )
        self.require_location(event.location, f"{path}/location", owner)
        if event_type in (EventType.CREATE_ELEMENTS, EventType.MOVE_ELEMENTS):
            self.require_elements(event.elements, f"{path}/elements", owner)
            self.require_container(event.container, f"{path}/container", owner)
        elif event_type in (EventType.REMOVE_ELEMENTS, EventType.RECONFIGURE_ELEMENTS):
            self.require_elements(event.elements, f"{path}/elements", owner)
        elif event_type == EventType.RECONFIGURE_ELEMENT:
            if self.require_element(event.element, f"{path}/element", owner):
                self.require_state(
                    event.element, event.state_index, f"{path}/stateIndex", owner
                )
        elif event_type == EventType.ADD_RESOURCES:
            self.require_element(event.container, f"{path}/container", owner)
            self.check_amounts(
                event.resources, f"{path}/resources", owner, non_negative=True
            )
        elif event_type == EventType.CONSUME_RESOURCES:
            self.require_element(event.source, f"{path}/source", owner)
            # negative amounts are produced
            self.check_amounts(event.resources, f"{path}/resources", owner)
        elif event_type == EventType.TRANSFER_RESOURCES:
            self.require_element(
                event.origin_container, f"{path}/originContainer", owner
            )
            self.require_element(
                event.destination_container, f"{path}/destinationContainer", owner
            )
            self.check_amounts(
                event.resources, f"{path}/resources", owner, non_negative=True
            )
        elif event_type == EventType.PROPULSIVE_BURN:
            self.require_elements(event.elements, f"{path}/elements", owner)
            if event.burn not in self.burns:
                self.error(
                    "unknown-burn",
                    f"{path}/burn",
                    f"{owner} references an unknown burn {event.burn}.",
                )
            self.check_burn_items(
                event.burn_stage_sequence, f"{path}/burnStageSequence", owner
            )
        elif event_type in (EventType.CREWED_EVA, EventType.CREWED_EXPLORATION):
            self.require_element(
                event.vehicle,
                f"{path}/vehicle",
                owner,
                CARRIER_TYPES,
                "a crew habitat (an element carrier)",
            )
            for index, element_state in enumerate(event.element_states):
                state_path = f"{path}/elementStates/{index}"
                if self.require_element(
                    element_state.element, f"{state_path}/element", owner
                ):
                    self.require_state(
                        element_state.element,
                        element_state.state_index,
                        f"{state_path}/stateIndex",
                        owner,
                    )
            self.check_amounts(
                event.additional_demands, f"{path}/additionalDemands", owner
            )
        elif event_type == EventType.FLIGHT_TRANSPORT:
            self.require_elements(event.elements, f"{path}/elements", owner)
            edge = self.require_edge(
                event.edge, s.EdgeType.FLIGHT, f"{path}/edge", owner
            )
            if edge is not None:
                self.check_departure(event, edge, path, owner)
        elif event_type == EventType.SPACE_TRANSPORT:
            self.require_elements(event.elements, f"{path}/elements", owner)
            edge = self.require_edge(
                event.edge, s.EdgeType.SPACE, f"{path}/edge", owner
            )
            if edge is not None:
                self.check_departure(event, edge, path, owner)
            edge_burns = {b.id for b in getattr(edge, "burns", [])}
            for index, sequence in enumerate(event.burn_stage_sequence):
                sequence_path = f"{path}/burnStageSequence/{index}"
                if edge is not None and sequence.burn not in edge_burns:
                    self.warning(
                        "burn-not-on-edge",
                        f"{sequence_path}/burn",
                        f"{owner} sequences a burn which is not a burn of "
                        f"{edge.name}, so the sequence is ignored.",
                    )
                self.check_burn_items(
                    sequence.actions, f"{sequence_path}/actions", owner
                )
        elif event_type == EventType.SURFACE_TRANSPORT:
            edge = self.require_edge(
                event.edge, s.EdgeType.SURFACE, f"{path}/edge", owner
            )
            if self.require_element(
                event.vehicle,
                f"{path}/vehicle",
                owner,
                (ElementType.SURFACE_VEHICLE,),
                "a surface vehicle",
            ):
                self.require_state(
                    event.vehicle,
                    event.transport_state,
                    f"{path}/transportState",
                    owner,
                )
            if edge is not None:
                self.check_departure(event, edge, path, owner, both_ends=True)

    def require_container(self, container_id: UUID, path: str, owner: str):
        """Checks that a container is a location or an element carrier."""
        if container_id in self.nodes or container_id in self.edges:
            return
        self.require_element(
            container_id,
            path,
            owner,
            CARRIER_TYPES,
            "a location or an element carrier",
        )

    def check_creations(self):
        """Warns of elements created by more than one event."""
        created: Dict[UUID, List[tuple]] = defaultdict(list)
        for mission_index, mission in enumerate(self.scenario.mission_list):
            for event_index, event in enumerate(mission.events):
                if EventType(event.type) != EventType.CREATE_ELEMENTS:
                    continue
                for element_id in event.elements:
                    created[element_id].append((mission_index, event_index))
        for element_id, sources in created.items():
            if len(sources) < 2 or element_id not in self.instances:
                continue
            self._mission, self._event = sources[1]
            self.warning(
                "created-twice",
                f"missionList/{sources[1][0]}/events/{sources[1][1]}",
                f"Element {self.name_of(element_id)} is created by {len(sources)} "
                "events.",
            )
        self._mission = self._event = None


def lint_scenario(scenario: s.Scenario) -> List[LintIssue]:
    """
    Checks a scenario for errors (which prevent or invalidate its
    simulation) and warnings (likely mistakes).

    Args:
        scenario (:obj:`Scenario`): The scenario.

    Returns:
        [:obj:`LintIssue`]: The issues, errors before warnings, each in the
        order of the scenario.
    """
    issues = _Linter(scenario).run()
    return sorted(issues, key=lambda i: i.severity != Severity.ERROR)


def errors(issues: Iterable[LintIssue]) -> List[LintIssue]:
    """Selects the errors of a list of issues."""
    return [i for i in issues if i.severity == Severity.ERROR]


def main(argv: Optional[List[str]] = None) -> int:
    """
    Prints the issues of scenario files.

    Returns:
        int: 1 if any scenario has errors (or does not match the object
        schema), otherwise 0.
    """
    parser = argparse.ArgumentParser(
        prog="python -m spacenet.lint", description="Checks SpaceNet scenarios."
    )
    parser.add_argument("paths", nargs="+", help="scenario files (JSON)")
    parser.add_argument("--errors-only", action="store_true", help="omit warnings")
    args = parser.parse_args(argv)
    status = 0
    for path in args.paths:
        try:
            with open(path, encoding="utf-8") as scenario_file:
                scenario = s.Scenario.model_validate_json(scenario_file.read())
        except (OSError, ValidationError) as error:
            print(f"{path}: {error}")
            status = 1
            continue
        issues = lint_scenario(scenario)
        if args.errors_only:
            issues = errors(issues)
        for issue in issues:
            print(f"{path}: {issue}")
        if errors(issues):
            status = 1
        error_count = len(errors(issues))
        print(f"{path}: {error_count} error(s), {len(issues) - error_count} warning(s)")
    return status


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
