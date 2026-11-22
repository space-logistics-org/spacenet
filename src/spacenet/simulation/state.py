"""
Simulation state.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from .. import schemas as s
from ..schemas.elements.element import ElementType
from ..schemas.events.burn import BurnStage
from ..schemas.events.event import EventType
from .demand_models import (
    SimCrewConsumablesDemandModel,
    SimDemandModel,
    SimRatedDemandModel,
    SimSparingByMassDemandModel,
    SimTimedImpulseDemandModel,
)
from .elements import (
    ElementContainer,
    OperationalState,
    PartApplication,
    SimCarrier,
    SimCrewMember,
    SimElement,
    SimPropulsionSystem,
    SimPropulsiveVehicle,
    SimResourceContainer,
    SimResourceTank,
    SimRoboticAgent,
    SimSurfaceVehicle,
)
from .errors import ScenarioError
from .events import (
    AddEvent,
    BurnEvent,
    CreateEvent,
    DemandEvent,
    EvaEvent,
    ExplorationProcess,
    FlightTransportEvent,
    ManifestEvent,
    MoveEvent,
    ReconfigureEvent,
    ReconfigureGroupEvent,
    RemoveEvent,
    SimEvent,
    SpaceTransportEvent,
    SurfaceTransportEvent,
    TransferEvent,
)
from .mission import SimMission
from .network import SimBurn, SimEdge, SimLocation, SimNetwork, SimNode
from .resources import Demand, DemandSet, SimResource
from .settings import Settings

SECONDS_PER_DAY = 24 * 60 * 60

_ELEMENT_CLASSES = {
    ElementType.ELEMENT: SimElement,
    ElementType.RESOURCE_CONTAINER: SimResourceContainer,
    ElementType.ELEMENT_CARRIER: SimCarrier,
    ElementType.HUMAN_AGENT: SimCrewMember,
    ElementType.ROBOTIC_AGENT: SimRoboticAgent,
    ElementType.PROPULSIVE_VEHICLE: SimPropulsiveVehicle,
    ElementType.SURFACE_VEHICLE: SimSurfaceVehicle,
}


def _days(duration: Optional[timedelta]) -> float:
    """Converts a duration to days."""
    return 0.0 if duration is None else duration.total_seconds() / SECONDS_PER_DAY


def _hours(duration: Optional[timedelta]) -> float:
    """Converts a duration to hours."""
    return 0.0 if duration is None else duration.total_seconds() / 3600


def _utc(date: datetime) -> datetime:
    """Interprets naive dates as coordinated universal time."""
    return date.replace(tzinfo=timezone.utc) if date.tzinfo is None else date


class State:
    """
    Simulation state.

    Builds the mutable objects (network, resources, elements, missions, and
    events) used by a simulator from an immutable scenario description.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, scenario: s.Scenario):
        #: Scenario from which this state was built.
        self.scenario = scenario
        #: Numerical precision and analysis options.
        self.settings = Settings(scenario.configuration)
        #: Date of the scenario start.
        self.start_date = scenario.start_date
        #: Specific resources by unique identifier.
        self.resources: Dict[UUID, SimResource] = {}
        self._generic_resources: Dict[tuple, SimResource] = {}
        #: Network of nodes and edges.
        self.network = SimNetwork()
        #: Instantiated elements by unique identifier.
        self.elements: Dict[UUID, SimElement] = {}
        #: Missions in scenario order.
        self.missions: List[SimMission] = []

        self._element_templates = {t.id: t for t in scenario.element_templates}
        self._template_indices = {
            t.id: i for i, t in enumerate(scenario.element_templates)
        }
        self._demand_model_templates = {t.id: t for t in scenario.demand_models}

        #: Events which load manifested containers in carriers.
        self.manifest_events: List[ManifestEvent] = []
        #: Descriptions of problems found while building the manifest.
        self.manifest_warnings: List[str] = []

        try:
            self._build_resources()
            self._build_network()
            self._build_elements()
            self._build_missions()
            self._build_manifest()
        except ScenarioError:
            raise
        except ValueError as error:
            raise ScenarioError(str(error)) from error

    # ------------------------------------------------------------------ time

    def get_time(self, date: datetime) -> float:
        """
        Gets the simulation time of a date.

        Args:
            date (:obj:`datetime.datetime`): The date.

        Returns:
            float: The time (days) relative to the scenario start.
        """
        delta = _utc(date) - _utc(self.start_date)
        return self.settings.round_time(delta.total_seconds() / SECONDS_PER_DAY)

    def get_date(self, time: float) -> datetime:
        """
        Gets the date of a simulation time.

        Args:
            time (float): The time (days) relative to the scenario start.

        Returns:
            :obj:`datetime.datetime`: The date.
        """
        return self.start_date + timedelta(days=time)

    # --------------------------------------------------------------- lookups

    def get_location(self, location_id: UUID) -> Optional[SimLocation]:
        """
        Get the network location matching a unique identifier.

        Args:
            location_id (:obj:`uuid.UUID`): the unique identifier

        Returns:
            :obj:`SimLocation`: The matching location if it exists, otherwise `None`.
        """
        return self.network.get_location(location_id)

    def get_element(self, element_id: UUID) -> Optional[SimElement]:
        """
        Get the element matching a unique identifier.

        Args:
            element_id (:obj:`uuid.UUID`): the unique identifier

        Returns:
            :obj:`SimElement`: The matching element if it exists, otherwise `None`.
        """
        return self.elements.get(element_id)

    def get_resource(
        self,
        resource: Union[UUID, s.ClassOfSupply],
        environment: s.Environment = s.Environment.UNPRESSURIZED,
    ) -> Optional[SimResource]:
        """
        Get the resource matching a unique identifier (specific resource) or
        a class of supply and environment (generic resource).

        Args:
            resource (:obj:`uuid.UUID` or :obj:`ClassOfSupply`): the unique
                identifier or class of supply
            environment (:obj:`Environment`): the environment of a generic resource

        Returns:
            :obj:`SimResource`: The matching resource if it exists, otherwise `None`.
        """
        if isinstance(resource, UUID):
            return self.resources.get(resource)
        key = (int(resource), s.Environment(environment))
        if key not in self._generic_resources:
            self._generic_resources[key] = SimResource.generic(
                self.settings, s.ClassOfSupply(resource), environment
            )
        return self._generic_resources[key]

    def _require_location(self, location_id: UUID, context: str) -> SimLocation:
        location = self.get_location(location_id)
        if location is None:
            raise ValueError(f"{context}: unknown location {location_id}")
        return location

    def _require_node(self, node_id: Optional[UUID], context: str) -> Optional[SimNode]:
        if node_id is None:
            return None
        node = self.get_location(node_id)
        if not isinstance(node, SimNode):
            raise ValueError(f"{context}: unknown node {node_id}")
        return node

    def _require_edge(self, edge_id: UUID, context: str, *edge_types) -> SimEdge:
        edge = self.get_location(edge_id)
        if not isinstance(edge, SimEdge):
            raise ValueError(f"{context}: unknown edge {edge_id}")
        if edge_types and edge.edge_type not in edge_types:
            raise ValueError(
                f"{context}: {edge} is a {edge.edge_type.value}, "
                f"expected a {' or '.join(t.value for t in edge_types)}"
            )
        return edge

    def _require_element(self, element_id: UUID, context: str) -> SimElement:
        element = self.get_element(element_id)
        if element is None:
            raise ValueError(f"{context}: unknown element {element_id}")
        return element

    def _require_elements(self, element_ids, context: str) -> List[SimElement]:
        return [self._require_element(i, context) for i in element_ids]

    def _require_container(self, container_id: UUID, context: str) -> ElementContainer:
        container = self.get_location(container_id)
        if container is None:
            container = self.get_element(container_id)
        if container is None:
            raise ValueError(f"{context}: unknown location or element {container_id}")
        if not isinstance(container, ElementContainer):
            raise ValueError(f"{context}: {container} cannot contain elements")
        return container

    # ------------------------------------------------------------- resources

    def _build_resources(self):
        for index, resource in enumerate(self.scenario.resource_list):
            self.resources[resource.id] = SimResource.from_schema(
                self.settings, resource, index
            )

    def _demand(self, amount, context: str) -> Demand:
        """Converts a resource amount (or rate) to a demand."""
        quantity = amount.amount if hasattr(amount, "amount") else amount.rate
        if hasattr(amount, "resource"):
            resource = self.get_resource(amount.resource)
            if resource is None:
                raise ValueError(f"{context}: unknown resource {amount.resource}")
        else:
            resource = self.get_resource(amount.class_of_supply, amount.environment)
        return Demand(resource, quantity)

    def _demands(self, amounts, context: str) -> DemandSet:
        return DemandSet(self._demand(a, context) for a in amounts or [])

    # --------------------------------------------------------------- network

    def _build_network(self):
        network = self.scenario.network
        for index, node in enumerate(network.nodes):
            self.network.add(
                SimNode(
                    id=node.id,
                    name=node.name,
                    description=node.description,
                    index=index,
                    node_type=node.type,
                    body=node.body_1,
                    illumination=getattr(node, "illumination", None),
                    max_night_duration=getattr(node, "max_night_duration", None),
                )
            )
        for index, edge in enumerate(network.edges):
            context = f"Edge {edge.name}"
            sim_edge = SimEdge(
                id=edge.id,
                name=edge.name,
                description=edge.description,
                index=len(network.nodes) + index,
                edge_type=edge.type,
                origin=self._require_node(edge.origin, context),
                destination=self._require_node(edge.destination, context),
                duration=self.settings.round_time(
                    _days(getattr(edge, "duration", None))
                ),
                burns=[
                    SimBurn(
                        id=b.id,
                        time=_days(b.time),
                        delta_v=b.delta_v,
                        propulsion_type=b.type,
                    )
                    for b in getattr(edge, "burns", [])
                ],
                distance=getattr(edge, "distance", 0.0),
                max_crew_size=getattr(edge, "max_crew", 0),
                max_cargo_mass=getattr(edge, "max_cargo", 0.0),
                cost_per_transport=edge.cost_per_transport,
                min_departure_interval=edge.min_departure_interval,
            )
            self.network.add(sim_edge)

    # -------------------------------------------------------------- elements

    def _build_elements(self):
        instances = self.scenario.instantiated_elements
        for index, instance in enumerate(instances):
            if instance.id in self.elements:
                raise ValueError(f"Duplicate instantiated element {instance.id}")
            self.elements[instance.id] = self._build_element(instance, index)
        # nest the initial contents of carriers
        for instance in instances:
            carrier = self.elements[instance.id]
            if not isinstance(carrier, SimCarrier):
                continue
            template = self._element_templates.get(instance.template_id)
            contents = getattr(instance, "contents", None) or getattr(
                template, "contents", None
            )
            for item in contents or []:
                child = self._get_content_element(getattr(item, "id", item), carrier)
                if child is carrier or carrier.is_inside(child):
                    raise ValueError(f"Element {carrier} cannot contain itself")
                carrier._attach(child)  # pylint: disable=protected-access
        # place elements initially located in the network
        for location in [*self.scenario.network.nodes, *self.scenario.network.edges]:
            sim_location = self.get_location(location.id)
            for item in location.contents:
                element = self._require_element(item.id, f"Location {location.name}")
                sim_location.add(element)
                self.network.register(element)

    def _get_content_element(self, element_id: UUID, carrier: SimCarrier) -> SimElement:
        """Gets an element nested in a carrier (instantiating templates as needed)."""
        if element_id in self.elements:
            return self.elements[element_id]
        template = self._element_templates.get(element_id)
        if template is None:
            raise ValueError(f"Element {carrier}: unknown content element {element_id}")
        child = self._build_element(template, len(self.elements))
        self.elements[child.id] = child
        return child

    def _build_element(self, instance, index: int) -> SimElement:
        """
        Builds an element from an instance (inheriting undefined attributes
        from its template) or directly from a template.
        """
        # pylint: disable=too-many-locals
        is_template = not hasattr(instance, "template_id")
        template = (
            instance
            if is_template
            else self._element_templates.get(instance.template_id)
        )
        element_id = uuid4() if is_template else instance.id

        def value(name, default=None):
            result = getattr(instance, name, None)
            if result is None and template is not None:
                result = getattr(template, name, None)
            return default if result is None else result

        context = f"Element {value('name', element_id)}"
        kwargs = {
            "id": element_id,
            "template_id": None if template is None else template.id,
            "name": value("name", str(element_id)),
            "description": value("description"),
            "class_of_supply": value("class_of_supply", s.ClassOfSupply.COS_0),
            "environment": value("environment", s.Environment.UNPRESSURIZED),
            "accommodation_mass": value("accommodation_mass", 0.0),
            "mass": value("mass", 0.0),
            "volume": value("volume", 0.0),
            "icon": value("icon"),
            "grid_connected": value("grid_connected", False),
            "unit_cost": value("unit_cost"),
            "design_life": value("design_life"),
            "index": index,
            "template_index": (
                len(self._template_indices)
                if template is None
                else self._template_indices.get(
                    template.id, len(self._template_indices)
                )
            ),
        }
        storage = value("energy_storage")
        if storage is not None:
            kwargs["energy_capacity"] = storage.capacity
            kwargs["energy"] = storage.charge
        element_type = ElementType(instance.type)
        if element_type in (ElementType.HUMAN_AGENT, ElementType.ROBOTIC_AGENT):
            kwargs["active_time_fraction"] = value("active_time_fraction")
        if element_type in (
            ElementType.RESOURCE_CONTAINER,
            ElementType.ELEMENT_CARRIER,
            ElementType.PROPULSIVE_VEHICLE,
            ElementType.SURFACE_VEHICLE,
        ):
            kwargs["max_cargo_mass"] = value("max_cargo_mass", 0.0)
            kwargs["max_cargo_volume"] = value("max_cargo_volume", 0.0)
            kwargs["cargo_environment"] = value(
                "cargo_environment", s.Environment.UNPRESSURIZED
            )
        if element_type == ElementType.RESOURCE_CONTAINER:
            kwargs["contents"] = [
                self._demand(a, context) for a in value("contents", [])
            ]
        if element_type in (
            ElementType.ELEMENT_CARRIER,
            ElementType.PROPULSIVE_VEHICLE,
            ElementType.SURFACE_VEHICLE,
        ):
            kwargs["max_crew_size"] = value("max_crew", 0)
        if element_type == ElementType.PROPULSIVE_VEHICLE:
            systems = value("propulsion_systems", [])
            tanks = {
                system.type: self._build_tank(system.fuel_tank, context)
                for system in systems
                if system.fuel_tank is not None
            }
            oxidizer_tanks = {
                system.type: self._build_tank(system.oxidizer_tank, context)
                for system in systems
                if system.oxidizer_tank is not None
            }
            kwargs["propulsion_systems"] = [
                SimPropulsionSystem(
                    system.type,
                    isp=system.isp,
                    fuel_tank=tanks.get(
                        system.type
                        if system.shared_fuel_tank is None
                        else system.shared_fuel_tank
                    ),
                    oxidizer_tank=oxidizer_tanks.get(
                        system.type
                        if system.shared_oxidizer_tank is None
                        else system.shared_oxidizer_tank
                    ),
                    mixture_ratio=system.mixture_ratio,
                )
                for system in systems
            ]
        if element_type == ElementType.SURFACE_VEHICLE:
            kwargs["max_speed"] = value("max_speed", 0.0)
            kwargs["fuel_consumption"] = value("fuel_consumption", 0.0)
            kwargs["energy_consumption"] = value("energy_consumption", 0.0)
            kwargs["max_crewed_duration"] = value("max_crewed_duration")
            kwargs["walk_back_distance"] = value("walk_back_distance")
            kwargs["fuel_tank"] = self._build_tank(value("fuel_tank"), context)

        element = _ELEMENT_CLASSES[element_type](self.settings, **kwargs)
        element.parts = [self._build_part(p, context) for p in value("parts", [])]
        for state in value("states", []):
            sim_state = OperationalState(
                id=state.id,
                name=state.name,
                description=state.description,
                state_type=state.type,
                demand_models=[
                    self._build_demand_model(m, element, context)
                    for m in state.demand_models
                ],
                power_consumption=state.power_consumption,
                power_generation=state.power_generation,
                generation_type=state.generation_type,
            )
            element.states.append(sim_state)
        state_index = value("current_state_index")
        if state_index is not None and state_index >= 0:
            if state_index >= len(element.states):
                raise ValueError(
                    f"{context}: invalid current state index {state_index}"
                )
            element.set_current_state(element.states[state_index])
        return element

    def _build_tank(
        self, tank: Optional[s.ResourceTank], context: str
    ) -> Optional[SimResourceTank]:
        """Builds a resource tank (e.g., the fuel tank of a vehicle)."""
        if tank is None:
            return None
        demand = self._demand(tank.contents, context)
        return SimResourceTank(
            self.settings,
            resource=demand.resource,
            amount=demand.raw_amount,
            max_amount=tank.max_amount,
            boiloff_rate=tank.boiloff_rate or 0.0,
        )

    def _build_part(self, part: s.Part, context: str) -> PartApplication:
        resource = self.get_resource(part.resource)
        if resource is None:
            raise ValueError(f"{context}: unknown part resource {part.resource}")
        return PartApplication(
            resource,
            mean_time_to_failure=_hours(part.mean_time_to_failure),
            mean_time_to_repair=_hours(part.mean_time_to_repair),
            mass_to_repair=part.mass_to_repair,
            quantity=part.quantity,
            duty_cycle=part.duty_cycle,
        )

    # --------------------------------------------------------- demand models

    def _build_demand_model(self, model, source, context: str) -> SimDemandModel:
        """
        Builds a demand model for a source (element or mission) from an
        instance (inheriting undefined attributes from its template).
        """
        template_id = getattr(model, "template_id", None)
        template = self._demand_model_templates.get(template_id)

        def value(name, default=None):
            result = getattr(model, name, None)
            if result is None and template is not None:
                result = getattr(template, name, None)
            return default if result is None else result

        kwargs = {
            "id": (
                template_id if template_id is not None else getattr(model, "id", None)
            ),
            "name": value("name"),
            "description": value("description"),
        }
        model_type = s.DemandModelType(model.type)
        if model_type == s.DemandModelType.TIMED_IMPULSE:
            return SimTimedImpulseDemandModel(
                demands=[self._demand(d, context) for d in value("demands", [])],
                **kwargs,
            )
        if model_type == s.DemandModelType.RATED:
            return SimRatedDemandModel(
                demand_rates=[self._demand(d, context) for d in value("demands", [])],
                **kwargs,
            )
        if model_type == s.DemandModelType.SPARING_BY_MASS:
            if not isinstance(source, SimElement):
                raise ValueError(f"{context}: sparing by mass requires an element")
            return SimSparingByMassDemandModel(
                source,
                unpressurized_spares_rate=value("unpressurized_spares_rate", 0.0),
                pressurized_spares_rate=value("pressurized_spares_rate", 0.0),
                parts_list_enabled=value("parts_list_enabled", True),
                **kwargs,
            )
        if not isinstance(source, SimMission):
            raise ValueError(f"{context}: crew consumables requires a mission")
        return SimCrewConsumablesDemandModel(
            source,
            **{key: value(key) for key in SimCrewConsumablesDemandModel.DEFAULTS},
            **kwargs,
        )

    # -------------------------------------------------------------- missions

    def _build_missions(self):
        for index, mission in enumerate(self.scenario.mission_list):
            context = f"Mission {mission.name}"
            try:
                sim_mission = SimMission(
                    self,
                    index=index,
                    name=mission.name,
                    start_date=mission.start_date,
                    start_time=self.get_time(mission.start_date),
                    origin=self._require_node(mission.origin, context),
                    destination=self._require_node(mission.destination, context),
                    return_origin=self._require_node(mission.return_origin, context),
                    return_destination=self._require_node(
                        mission.return_destination, context
                    ),
                )
                for event_index, event in enumerate(mission.events):
                    try:
                        sim_event = self._build_event(event, context)
                    except ValueError as error:
                        raise ScenarioError(str(error), index, event_index) from error
                    sim_event.mission_index = index
                    sim_event.event_index = event_index
                    sim_mission.events.append(sim_event)
                sim_mission.demand_models = [
                    self._build_demand_model(m, sim_mission, context)
                    for m in mission.demand_models
                ]
            except ScenarioError:
                raise
            except ValueError as error:
                raise ScenarioError(str(error), index) from error
            self.missions.append(sim_mission)
        for sim_mission in self.missions:
            sim_mission.crew_size  # pylint: disable=pointless-statement

    # -------------------------------------------------------------- manifest

    def _build_manifest(self):
        """
        Builds the resource containers of the scenario manifest and the
        events which load them in carriers. Entries which do not match the
        scenario are skipped with a warning.
        """
        manifest = self.scenario.manifest
        if manifest is None:
            return
        containers: Dict[UUID, SimResourceContainer] = {}
        for stored in manifest.containers:
            if stored.id in self.elements:
                self.manifest_warnings.append(
                    f"Manifest container {stored.name} duplicates an element."
                )
                continue
            container = SimResourceContainer(
                self.settings,
                id=stored.id,
                name=stored.name,
                class_of_supply=s.ClassOfSupply.COS_501,
                environment=stored.environment,
                mass=stored.mass,
                volume=stored.volume,
                max_cargo_mass=stored.max_cargo_mass,
                max_cargo_volume=stored.max_cargo_volume,
                cargo_environment=stored.cargo_environment,
                index=len(self.elements),
                template_index=len(self._template_indices),
            )
            for packed in stored.contents:
                reference = packed.resource
                if reference.resource is None:
                    resource = self.get_resource(
                        reference.class_of_supply, reference.environment
                    )
                else:
                    resource = self.get_resource(reference.resource)
                if resource is None:
                    self.manifest_warnings.append(
                        f"Manifest container {stored.name} references an "
                        f"unknown resource {reference.resource}."
                    )
                elif not container.add(resource, packed.amount):
                    self.manifest_warnings.append(
                        f"{packed.amount:g} {resource.units} of {resource} could "
                        f"not be added to manifest container {stored.name}."
                    )
            containers[stored.id] = container
            self.elements[stored.id] = container
        for load in manifest.loads:
            reference = load.supply_edge
            edge = self.get_location(reference.edge)
            carrier = self.get_element(load.carrier)
            if not isinstance(edge, SimEdge) or not isinstance(carrier, SimCarrier):
                self.manifest_warnings.append(
                    "Manifest references an unknown transport or carrier."
                )
                continue
            loaded = [containers[i] for i in load.containers if i in containers]
            if len(loaded) < len(load.containers):
                self.manifest_warnings.append(
                    f"Manifest references unknown containers for {carrier}."
                )
            if loaded:
                self.manifest_events.append(
                    ManifestEvent(
                        time=self.settings.round_time(reference.start_time),
                        priority=0,
                        location=(
                            edge.destination if reference.reversed else edge.origin
                        ),
                        carrier=carrier,
                        containers=loaded,
                    )
                )

    def _get_state(
        self, element: SimElement, state_index: Optional[int], context: str
    ) -> Optional[OperationalState]:
        if state_index is None or state_index < 0:
            return None
        if state_index >= len(element.states):
            raise ValueError(
                f"{context}: invalid state index {state_index} for {element}"
            )
        return element.states[state_index]

    def _get_state_map(self, element_states, context: str):
        state_map = {}
        for element_state in element_states:
            element = self._require_element(element_state.element, context)
            state_map[element] = self._get_state(
                element, element_state.state_index, context
            )
        return state_map

    def _get_burn(self, burn_id: UUID, context: str) -> SimBurn:
        for edge in self.network.edges:
            for burn in edge.burns:
                if burn.id == burn_id:
                    return burn
        raise ValueError(f"{context}: unknown burn {burn_id}")

    def _get_burn_stage_items(self, actions, context: str):
        return [
            (BurnStage(a.type), self._require_element(a.element, context))
            for a in actions
        ]

    def _build_event(self, event, mission_context: str) -> SimEvent:
        """Builds a simulation event from its schema."""
        # pylint: disable=too-many-return-statements,too-many-branches
        context = f"{mission_context}, event {event.name}"
        kwargs = {
            "name": event.name,
            "priority": event.priority,
            "mission_time": _days(event.mission_time),
            "location": self._require_location(event.location, context),
        }
        event_type = EventType(event.type)
        if event_type == EventType.CREATE_ELEMENTS:
            return CreateEvent(
                elements=self._require_elements(event.elements, context),
                container=self._require_container(event.container, context),
                **kwargs,
            )
        if event_type == EventType.MOVE_ELEMENTS:
            return MoveEvent(
                elements=self._require_elements(event.elements, context),
                container=self._require_container(event.container, context),
                **kwargs,
            )
        if event_type == EventType.REMOVE_ELEMENTS:
            return RemoveEvent(
                elements=self._require_elements(event.elements, context), **kwargs
            )
        if event_type == EventType.RECONFIGURE_ELEMENT:
            element = self._require_element(event.element, context)
            return ReconfigureEvent(
                element=element,
                state=self._get_state(element, event.state_index, context),
                **kwargs,
            )
        if event_type == EventType.RECONFIGURE_ELEMENTS:
            return ReconfigureGroupEvent(
                elements=self._require_elements(event.elements, context),
                state_type=event.state_type,
                **kwargs,
            )
        if event_type == EventType.ADD_RESOURCES:
            return AddEvent(
                demands=self._demands(event.resources, context),
                container=self._require_element(event.container, context),
                **kwargs,
            )
        if event_type == EventType.CONSUME_RESOURCES:
            return DemandEvent(
                demands=self._demands(event.resources, context),
                element=self._require_element(event.source, context),
                **kwargs,
            )
        if event_type == EventType.TRANSFER_RESOURCES:
            return TransferEvent(
                demands=self._demands(event.resources, context),
                origin_container=self._require_element(event.origin_container, context),
                destination_container=self._require_element(
                    event.destination_container, context
                ),
                origin_tank=event.origin_tank,
                destination_tank=event.destination_tank,
                transfer_mode=event.transfer_mode,
                loss_fraction=event.loss_fraction or 0.0,
                **kwargs,
            )
        if event_type == EventType.PROPULSIVE_BURN:
            return BurnEvent(
                elements=self._require_elements(event.elements, context),
                burn=self._get_burn(event.burn, context),
                burn_stage_sequence=self._get_burn_stage_items(
                    event.burn_stage_sequence, context
                ),
                **kwargs,
            )
        if event_type == EventType.CREWED_EVA:
            return EvaEvent(
                vehicle=self._require_element(event.vehicle, context),
                eva_duration=_hours(event.eva_duration),
                state_map=self._get_state_map(event.element_states, context),
                demands=self._demands(event.additional_demands, context),
                **kwargs,
            )
        if event_type == EventType.CREWED_EXPLORATION:
            return ExplorationProcess(
                vehicle=self._require_element(event.vehicle, context),
                eva_duration=_hours(event.eva_duration),
                duration=_days(event.duration),
                eva_per_week=event.eva_per_week,
                state_map=self._get_state_map(event.element_states, context),
                demands=self._demands(event.additional_demands, context),
                **kwargs,
            )
        if event_type == EventType.FLIGHT_TRANSPORT:
            return FlightTransportEvent(
                edge=self._require_edge(event.edge, context, s.EdgeType.FLIGHT),
                elements=self._require_elements(event.elements, context),
                **kwargs,
            )
        if event_type == EventType.SPACE_TRANSPORT:
            edge = self._require_edge(event.edge, context, s.EdgeType.SPACE)
            sequences = {
                sequence.burn: self._get_burn_stage_items(sequence.actions, context)
                for sequence in event.burn_stage_sequence
            }
            return SpaceTransportEvent(
                edge=edge,
                elements=self._require_elements(event.elements, context),
                burn_stage_sequence=[sequences.get(b.id, []) for b in edge.burns],
                **kwargs,
            )
        if event_type == EventType.SURFACE_TRANSPORT:
            vehicle = self._require_element(event.vehicle, context)
            return SurfaceTransportEvent(
                edge=self._require_edge(event.edge, context, s.EdgeType.SURFACE),
                vehicle=vehicle,
                transport_state=self._get_state(
                    vehicle, event.transport_state, context
                ),
                speed=event.speed,
                duty_cycle=event.duty_cycle,
                **kwargs,
            )
        raise ValueError(f"{context}: unsupported event type {event.type}")
