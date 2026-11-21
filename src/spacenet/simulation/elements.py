"""
Elements (objects that persist over time) used during simulation.
"""

# pylint: disable=too-many-lines

import math
from bisect import insort
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from ..schemas import ClassOfSupply, Environment, StateType
from ..schemas.elements.element import ElementType
from ..schemas.elements.propulsion import PropulsionType, TankSelector
from .records import PropellantFlowKind, SimScavenge
from .resources import Demand, DemandSet, SimResource
from .settings import Settings

if TYPE_CHECKING:  # pragma: no cover
    from .demand_models import SimDemandModel
    from .network import SimLocation
    from .simulator import Simulator


class PartApplication:
    """
    The application of a part (resource) within an element.
    """

    def __init__(
        self,
        part: SimResource,
        *,
        mean_time_to_failure: float = 0.0,
        mean_time_to_repair: float = 0.0,
        mass_to_repair: float = 0.0,
        quantity: float = 1.0,
        duty_cycle: float = 1.0,
    ):
        self.part = part
        #: Mean operating time (hours) to failure (0 if the part does not fail).
        self.mean_time_to_failure = mean_time_to_failure or 0.0
        #: Mean crew time (hours) to repair (0 if the part is not repairable).
        self.mean_time_to_repair = mean_time_to_repair or 0.0
        #: Mass (kg, generic COS 4) required to repair one unit.
        self.mass_to_repair = mass_to_repair or 0.0
        self.quantity = part.settings.round_demand(quantity)
        self.duty_cycle = duty_cycle

    @property
    def unit_mean_time_to_repair(self) -> float:
        """The mean crew time (hours) to repair per unit mass (kg) of the part."""
        return self.mean_time_to_repair / self.part.unit_mass

    def __str__(self):
        return f"{self.part} ({int(self.quantity)})"


class OperationalState:
    """
    An operational state of an element which generates demands.
    """

    def __init__(
        self,
        *,
        name: str,
        state_type: StateType = StateType.ACTIVE,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
        demand_models: Optional[List["SimDemandModel"]] = None,
    ):
        self.id = id if id is not None else uuid4()
        self.name = name
        self.description = description
        self.state_type = StateType(state_type)
        self.demand_models = list(demand_models) if demand_models is not None else []

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        """
        Generates the demands of this state over a duration.

        Args:
            duration (float): The duration (days).
            simulator (:obj:`Simulator`): The simulator.

        Returns:
            :obj:`DemandSet`: The aggregated demands.
        """
        demands = DemandSet()
        for model in self.demand_models:
            demands.add_all(model.generate_demands(duration, simulator))
        return demands

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"OperationalState({self.name!r}, {self.state_type.value!r})"


class ElementContainer:
    """
    Mixin for objects that contain elements, i.e., locations and carriers.
    """

    def _init_contents(self):
        # pylint: disable=attribute-defined-outside-init
        self._contents: List["SimElement"] = []

    @property
    def contents(self) -> Tuple["SimElement", ...]:
        """The directly contained elements (ordered by name)."""
        return tuple(self._contents)

    @property
    def complete_contents(self) -> List["SimElement"]:
        """All contained elements including the contents of nested carriers."""
        elements = []

        def recursive_add(element):
            elements.append(element)
            if isinstance(element, ElementContainer):
                for child in element.contents:
                    recursive_add(child)

        for element in self._contents:
            recursive_add(element)
        return sorted(elements, key=lambda e: e.sort_key)

    @property
    def cargo_mass(self) -> float:
        """The total mass (kg) of contained elements, excluding crew members."""
        return sum(
            e.total_mass for e in self._contents if not isinstance(e, SimCrewMember)
        )

    @property
    def cargo_volume(self) -> float:
        """The volume (m^3) of contained elements, excluding crew members."""
        return sum(e.volume for e in self._contents if not isinstance(e, SimCrewMember))

    @property
    def crew_size(self) -> int:
        """The number of directly contained crew members."""
        return sum(1 for e in self._contents if isinstance(e, SimCrewMember))

    @property
    def total_crew_size(self) -> int:
        """The number of crew members including those in nested carriers."""
        crew = 0
        for element in self._contents:
            if isinstance(element, SimCrewMember):
                crew += 1
            elif isinstance(element, SimCarrier):
                crew += element.total_crew_size
        return crew

    def _attach(self, element: "SimElement"):
        """Places an element directly inside this container (no checks)."""
        if element.container is not None and element.container is not self:
            element.container.remove(element)
        if not any(e is element for e in self._contents):
            insort(self._contents, element, key=lambda e: e.sort_key)
        element.container = self

    def _detach(self, element: "SimElement") -> bool:
        """Takes an element out of this container."""
        for i, other in enumerate(self._contents):
            if other is element:
                del self._contents[i]
                element.container = None
                return True
        return False

    def contains(self, element: "SimElement") -> bool:
        """
        Checks if an element is directly inside this container.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element is directly contained.
        """
        return any(e is element for e in self._contents)


class SimElement:
    """
    A generic element.
    """

    element_type = ElementType.ELEMENT

    def __init__(
        self,
        settings: Settings,
        *,
        name: str,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        template_id: Optional[UUID] = None,
        description: Optional[str] = None,
        class_of_supply: ClassOfSupply = ClassOfSupply.COS_0,
        environment: Environment = Environment.UNPRESSURIZED,
        accommodation_mass: float = 0.0,
        mass: float = 0.0,
        volume: float = 0.0,
        states: Optional[List[OperationalState]] = None,
        current_state: Optional[OperationalState] = None,
        parts: Optional[List[PartApplication]] = None,
        icon: Optional[str] = None,
        index: int = 0,
        template_index: int = 0,
    ):
        self.settings = settings
        self.id = id if id is not None else uuid4()
        self.template_id = template_id
        self.name = name
        self.description = description
        self.class_of_supply = ClassOfSupply(class_of_supply)
        self._environment = Environment(environment)
        self._accommodation_mass = accommodation_mass or 0.0
        self._mass = mass or 0.0
        self._volume = volume or 0.0
        self.states: List[OperationalState] = list(states) if states is not None else []
        self.current_state: Optional[OperationalState] = None
        self.parts: List[PartApplication] = list(parts) if parts is not None else []
        self.icon = icon
        self.index = index
        self.template_index = template_index
        self.container: Optional[ElementContainer] = None
        if current_state is not None:
            self.set_current_state(current_state)

    @property
    def sort_key(self) -> tuple:
        """The key which establishes element ordering (by name)."""
        return (self.name, self.template_index, self.index, str(self.id))

    @property
    def environment(self) -> Environment:
        """The required stowage environment."""
        if self.settings.environment_constrained:
            return self._environment
        return Environment.UNPRESSURIZED

    @property
    def accommodation_mass(self) -> float:
        """The mass (kg) of secondary structure required for stowage."""
        return self.settings.round_mass(self._accommodation_mass)

    @property
    def mass(self) -> float:
        """The (dry) mass (kg) of this element."""
        return self.settings.round_mass(self._mass)

    @mass.setter
    def mass(self, mass: float):
        self._mass = mass

    @property
    def volume(self) -> float:
        """The volume (m^3) of this element."""
        return self.settings.round_volume(self._volume)

    @volume.setter
    def volume(self, volume: float):
        self._volume = volume

    @property
    def total_mass(self) -> float:
        """The total mass (kg) including any nested elements and resources."""
        return self.get_total_mass()

    @property
    def total_volume(self) -> float:
        """The total volume (m^3) of this element."""
        return self.settings.round_volume(self.volume)

    def _is_scavenged(self) -> bool:
        return (
            self.settings.scavenge_spares
            and self.current_state is not None
            and self.current_state.state_type == StateType.DECOMMISSIONED
        )

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        """
        Gets the total mass, optionally restricted to a class of supply.

        Args:
            class_of_supply (:obj:`ClassOfSupply`): The class of supply to
                include (default: all).

        Returns:
            float: The total mass (kg).
        """
        if class_of_supply is None:
            return self.settings.round_mass(self.mass)
        mass = 0.0
        if self._is_scavenged():
            parts_mass = 0.0
            for part in self.parts:
                parts_mass += part.quantity * part.part.unit_mass
                if part.part.class_of_supply.is_instance_of(class_of_supply):
                    mass += part.quantity * part.part.unit_mass
            if self.class_of_supply.is_instance_of(class_of_supply):
                mass += max(0.0, self.mass - parts_mass)
        elif self.class_of_supply.is_instance_of(class_of_supply):
            mass += self.mass
        return self.settings.round_mass(mass)

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        """
        Generates the demands of this element in its current state.

        Args:
            duration (float): The duration (days).
            simulator (:obj:`Simulator`): The simulator.

        Returns:
            :obj:`DemandSet`: The aggregated demands.
        """
        if self.current_state is None:
            return DemandSet()
        return self.current_state.generate_demands(duration, simulator)

    def satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        """
        Attempts to satisfy demands using this element. A generic element can
        only satisfy demands for parts by scavenging when decommissioned.

        Args:
            demands (:obj:`DemandSet`): The demands (modified in place).
            simulator (:obj:`Simulator`): The simulator.
        """
        if not self._is_scavenged():
            return
        for application in self.parts:
            for demand in demands:
                if application.part != demand.resource or demand.amount <= 0:
                    continue
                if application.quantity <= 0:
                    continue
                if demand.amount > application.quantity:
                    simulator.scavenged_parts.append(
                        SimScavenge(
                            simulator.time,
                            application.part,
                            application.quantity,
                            self.location,
                            self,
                        )
                    )
                    demand.amount = demand.amount - application.quantity
                    application.quantity = 0
                else:
                    simulator.scavenged_parts.append(
                        SimScavenge(
                            simulator.time,
                            application.part,
                            demand.amount,
                            self.location,
                            self,
                        )
                    )
                    application.quantity = application.quantity - demand.amount
                    demand.amount = 0
                    break

    def set_current_state(self, state: Optional[OperationalState]) -> bool:
        """
        Sets the current operational state.

        Args:
            state (:obj:`OperationalState`): The new state which must be one
                of the states of this element (or `None` for a stateless element).

        Returns:
            bool: True, if the state was changed.
        """
        if not self.states and state is None:
            self.current_state = None
            return True
        if any(s is state for s in self.states):
            self.current_state = state
            return True
        return False

    @property
    def location(self) -> Optional["SimLocation"]:
        """The network location (node or edge), or `None` if not yet created."""
        container = self.container
        while isinstance(container, SimElement):
            container = container.container
        return container

    def is_inside(self, container: ElementContainer) -> bool:
        """
        Checks if this element is (recursively) inside a container.

        Args:
            container (:obj:`ElementContainer`): The location or carrier.

        Returns:
            bool: True, if this element is inside the container.
        """
        parent = self.container
        while parent is not None:
            if parent is container:
                return True
            parent = getattr(parent, "container", None)
        return False

    def __eq__(self, other):
        return isinstance(other, SimElement) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"


class SimAgent(SimElement):
    """
    An element which can perform work.
    """

    def __init__(
        self, settings: Settings, *, active_time_fraction: float = 0.667, **kwargs
    ):
        super().__init__(settings, **kwargs)
        #: Fraction of time (0 to 1) available for productive activities.
        self.active_time_fraction = (
            0.667 if active_time_fraction is None else active_time_fraction
        )


class SimCrewMember(SimAgent):
    """
    A human agent, i.e., a crew member.
    """

    element_type = ElementType.HUMAN_AGENT

    @property
    def available_time_fraction(self) -> float:
        """Fraction of time (0 to 1) available for productive activities."""
        return self.active_time_fraction


class SimRoboticAgent(SimAgent):
    """
    A robotic agent. Robotic agents do not count as crew.
    """

    element_type = ElementType.ROBOTIC_AGENT


class SimResourceContainer(SimElement):
    """
    A container for (possibly multiple types of) resources.
    """

    element_type = ElementType.RESOURCE_CONTAINER

    def __init__(
        self,
        settings: Settings,
        *,
        max_cargo_mass: float = 0.0,
        max_cargo_volume: float = 0.0,
        cargo_environment: Environment = Environment.UNPRESSURIZED,
        contents: Optional[List[Demand]] = None,
        **kwargs,
    ):
        super().__init__(settings, **kwargs)
        self._max_cargo_mass = max_cargo_mass or 0.0
        self._max_cargo_volume = max_cargo_volume or 0.0
        self.cargo_environment = Environment(cargo_environment)
        self._resources: Dict[SimResource, float] = {}
        for demand in contents or []:
            self._resources[demand.resource] = (
                self._resources.get(demand.resource, 0.0) + demand.amount
            )

    @property
    def contents(self) -> Dict[SimResource, float]:
        """The contained resource amounts (units) in resource order."""
        return {
            r: self._resources[r]
            for r in sorted(self._resources, key=lambda r: r.sort_key)
        }

    @property
    def max_cargo_mass(self) -> float:
        """The cargo mass capacity (kg)."""
        return self.settings.round_mass(self._max_cargo_mass)

    @property
    def max_cargo_volume(self) -> float:
        """The cargo volume capacity (m^3)."""
        return self.settings.round_volume(self._max_cargo_volume)

    @property
    def cargo_mass(self) -> float:
        """The mass (kg) of contained resources."""
        return self.settings.round_mass(
            sum(r.unit_mass * amount for r, amount in self._resources.items())
        )

    @property
    def cargo_volume(self) -> float:
        """The volume (m^3) of contained resources."""
        return self.settings.round_volume(
            sum(r.unit_volume * amount for r, amount in self._resources.items())
        )

    def get_amount(self, resource: SimResource) -> float:
        """
        Gets the contained amount of a resource.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            float: The contained amount (units).
        """
        return self._resources.get(resource, 0.0)

    def get_space(self, resource: SimResource) -> float:
        """
        Gets the amount of a resource which can be added within capacity
        constraints.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            float: The amount (units) which can be added.
        """
        if (
            self.settings.environment_constrained
            and self.cargo_environment != resource.environment
        ):
            return 0.0
        space = math.inf
        if resource.unit_mass > 0:
            space = (self._max_cargo_mass - self.cargo_mass) / resource.unit_mass
        if self.settings.volume_constrained and resource.unit_volume > 0:
            space = min(
                space,
                (self._max_cargo_volume - self.cargo_volume) / resource.unit_volume,
            )
        return max(0.0, space)

    def can_add(self, resource: SimResource, amount: float) -> bool:
        """
        Checks if a resource amount can be added within capacity constraints.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource can be added.
        """
        if (
            self.cargo_mass + resource.unit_mass * amount - self._max_cargo_mass
            > self.settings.mass_precision / 2
        ):
            return False  # mass constrained
        if (
            self.settings.volume_constrained
            and self.cargo_volume
            + resource.unit_volume * amount
            - self._max_cargo_volume
            > self.settings.volume_precision / 2
        ):
            return False  # volume constrained
        if (
            self.settings.environment_constrained
            and self.cargo_environment != resource.environment
        ):
            return False  # environment constrained
        return True

    def add(self, resource: SimResource, amount: float) -> bool:
        """
        Adds a resource amount to this container.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource was added.
        """
        if not self.can_add(resource, amount):
            return False
        self._resources[resource] = self._resources.get(resource, 0.0) + amount
        return True

    def remove(self, resource: SimResource, amount: float) -> bool:
        """
        Removes a resource amount from this container.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource was removed.
        """
        if resource not in self._resources:
            return False
        if self._resources[resource] > amount:
            self._resources[resource] -= amount
            return True
        if self._resources[resource] == amount:
            del self._resources[resource]
            return True
        return False

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        if class_of_supply is None:
            return self.settings.round_mass(super().get_total_mass() + self.cargo_mass)
        amount = super().get_total_mass(class_of_supply)
        for resource, quantity in self._resources.items():
            if resource.class_of_supply.is_instance_of(class_of_supply):
                amount += quantity * resource.unit_mass
        return self.settings.round_mass(amount)

    def satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        super().satisfy_demands(demands, simulator)
        for demand in demands:
            if demand.amount > 0:  # consumption
                is_exploration_item = demand.resource.class_of_supply.is_instance_of(
                    ClassOfSupply.COS_6
                )
                for resource in list(self.contents):
                    if not resource.is_substitutable_for(demand.resource):
                        continue
                    if demand.amount >= self._resources[resource]:
                        demand.amount = demand.amount - self._resources[resource]
                        if not is_exploration_item:
                            self._resources[resource] = 0.0
                    else:
                        if not is_exploration_item:
                            self._resources[resource] -= demand.amount
                        demand.amount = 0
                        break
            else:  # production
                for resource in list(self.contents):
                    if resource != demand.resource:
                        continue
                    capacity = self.max_cargo_mass - self.cargo_mass
                    if -demand.amount > capacity:
                        demand.amount = demand.amount + capacity
                        self._resources[resource] += capacity
                    else:
                        self._resources[resource] += -demand.amount
                        demand.amount = 0
        demands.clean()


class SimResourceTank(SimElement):
    """
    A container for a single type of resource, e.g., a vehicle fuel tank.
    """

    element_type = None

    def __init__(
        self,
        settings: Settings,
        *,
        resource: Optional[SimResource] = None,
        amount: float = 0.0,
        max_amount: float = 0.0,
        name: str = "Fuel Tank",
        boiloff_rate: float = 0.0,
        **kwargs,
    ):
        super().__init__(settings, name=name, **kwargs)
        self.resource = resource
        self._amount = amount or 0.0
        self._max_amount = max_amount or 0.0
        #: Fraction of the capacity lost per day (e.g., cryogenic boiloff).
        self.boiloff_rate = boiloff_rate or 0.0
        #: Key of this tank within its vehicle, e.g., "OMS Fuel" or "Fuel".
        self.key = "Fuel"
        #: Role of this tank within its vehicle ("Fuel" or "Oxidizer").
        self.role = "Fuel"

    @property
    def vehicle(self) -> Optional["SimElement"]:
        """The vehicle of this (integral) tank, if any."""
        return self.container if isinstance(self.container, SimElement) else None

    def apply_boiloff(self, days: float) -> float:
        """
        Removes the resource lost to boiloff over a duration.

        Args:
            days (float): The duration (days).

        Returns:
            float: The amount (units) lost.
        """
        if self.boiloff_rate <= 0 or days <= 0 or self._amount <= 0:
            return 0.0
        loss = min(self._amount, self.boiloff_rate * self._max_amount * days)
        self._amount -= loss
        return loss

    @property
    def amount(self) -> float:
        """The contained resource amount (units)."""
        return self.settings.round_demand(self._amount)

    @amount.setter
    def amount(self, amount: float):
        self._amount = amount

    @property
    def max_amount(self) -> float:
        """The resource amount capacity (units)."""
        return self.settings.round_demand(self._max_amount)

    @max_amount.setter
    def max_amount(self, max_amount: float):
        self._max_amount = max_amount

    @property
    def contents(self) -> Dict[SimResource, float]:
        """The contained resource amounts (units)."""
        return {} if self.resource is None else {self.resource: self._amount}

    @property
    def cargo_environment(self) -> Environment:
        """The stowage environment provided by this tank."""
        return Environment.UNPRESSURIZED

    @property
    def cargo_mass(self) -> float:
        """The mass (kg) of the contained resource."""
        if self.resource is None:
            return 0.0
        return self.settings.round_mass(self._amount * self.resource.unit_mass)

    @property
    def cargo_volume(self) -> float:
        """The volume (m^3) of the contained resource."""
        if self.resource is None:
            return 0.0
        return self.settings.round_volume(self._amount * self.resource.unit_volume)

    @property
    def max_cargo_mass(self) -> float:
        """The cargo mass capacity (kg)."""
        if self.resource is None:
            return 0.0
        return self.settings.round_mass(self._max_amount * self.resource.unit_mass)

    @property
    def max_cargo_volume(self) -> float:
        """The cargo volume capacity (m^3)."""
        if self.resource is None:
            return 0.0
        return self.settings.round_volume(self._max_amount * self.resource.unit_volume)

    def get_amount(self, resource: SimResource) -> float:
        """
        Gets the contained amount of a resource.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            float: The contained amount (units).
        """
        return self._amount if resource == self.resource else 0.0

    def get_space(self, resource: SimResource) -> float:
        """
        Gets the amount of a resource which can be added within capacity.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            float: The amount (units) which can be added.
        """
        if self.resource is not None and self.resource != resource:
            return 0.0
        return max(0.0, self._max_amount - self._amount)

    def can_add(self, resource: SimResource, amount: float) -> bool:
        """
        Checks if a resource amount can be added within capacity constraints.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource can be added.
        """
        if self.resource is not None and self.resource != resource:
            return False
        return not (
            self._amount + amount - self._max_amount
            > self.settings.demand_precision / 2
        )

    def add(self, resource: SimResource, amount: float) -> bool:
        """
        Adds a resource amount to this tank.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource was added.
        """
        if not self.can_add(resource, amount):
            return False
        if self.resource is None:
            self.resource = resource
        self._amount += amount
        return True

    def remove(self, resource: SimResource, amount: float) -> bool:
        """
        Removes a resource amount from this tank.

        Args:
            resource (:obj:`SimResource`): The resource.
            amount (float): The amount (units).

        Returns:
            bool: True, if the resource was removed.
        """
        if self.resource is None or self.resource != resource:
            return False
        if self._amount - amount >= 0:
            self._amount -= amount
            return True
        return False

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        if class_of_supply is None:
            return self.settings.round_mass(super().get_total_mass() + self.cargo_mass)
        mass = super().get_total_mass(class_of_supply)
        if self.resource is not None and self.resource.class_of_supply.is_instance_of(
            class_of_supply
        ):
            mass += self.resource.unit_mass * self.amount
        return self.settings.round_mass(mass)

    def satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        before = self._amount
        self._satisfy_demands(demands, simulator)
        if self._amount != before and simulator is not None:
            simulator.record_propellant(
                self,
                PropellantFlowKind.CONSUMED,
                before - self._amount,
            )

    def _satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        super().satisfy_demands(demands, simulator)
        for demand in demands:
            if not demand.resource.is_substitutable_for(self.resource):
                continue
            if demand.amount > 0:  # consumption
                if demand.amount > self._amount:
                    demand.amount = demand.amount - self._amount
                    self._amount = 0.0
                else:
                    self._amount -= demand.amount
                    demand.amount = 0
            else:  # production
                if -demand.amount > self._max_amount - self._amount:
                    demand.amount = demand.amount + (self._max_amount - self._amount)
                    self._amount = self._max_amount
                else:
                    self._amount += -demand.amount
                    demand.amount = 0
        demands.clean()

    def __str__(self):
        if self.resource is None:
            return f"{self.name} ({self.amount:.1f} / {self.max_amount:.1f})"
        return (
            f"{self.name} ({self.amount:.1f} / {self.max_amount:.1f} "
            f"{self.resource.units} {self.resource})"
        )


class SimCarrier(SimElement, ElementContainer):
    """
    An element which can contain other elements.
    """

    element_type = ElementType.ELEMENT_CARRIER

    def __init__(
        self,
        settings: Settings,
        *,
        max_cargo_mass: float = 0.0,
        max_cargo_volume: float = 0.0,
        cargo_environment: Environment = Environment.UNPRESSURIZED,
        max_crew_size: int = 0,
        **kwargs,
    ):
        super().__init__(settings, **kwargs)
        self._init_contents()
        self._max_cargo_mass = max_cargo_mass or 0.0
        self._max_cargo_volume = max_cargo_volume or 0.0
        self.cargo_environment = Environment(cargo_environment)
        self.max_crew_size = max_crew_size or 0

    @property
    def max_cargo_mass(self) -> float:
        """The cargo mass capacity (kg)."""
        return self.settings.round_mass(self._max_cargo_mass)

    @property
    def max_cargo_volume(self) -> float:
        """The cargo volume capacity (m^3)."""
        return self.settings.round_volume(self._max_cargo_volume)

    @property
    def cargo_volume(self) -> float:
        return self.settings.round_volume(super().cargo_volume)

    def can_add(self, element: SimElement) -> bool:
        """
        Checks if an element can be added within capacity constraints.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element can be added.
        """
        if self.contains(element):
            return True
        if isinstance(element, SimCrewMember):
            return self.crew_size < self.max_crew_size
        if (
            self.cargo_mass + element.total_mass - self.max_cargo_mass
            > self.settings.mass_precision / 2
        ):
            return False  # mass constrained
        if (
            self.settings.volume_constrained
            and self.cargo_volume + element.volume - self.max_cargo_volume
            > self.settings.volume_precision / 2
        ):
            return False  # volume constrained
        if (
            self.settings.environment_constrained
            and element.environment == Environment.PRESSURIZED
            and self.cargo_environment == Environment.UNPRESSURIZED
        ):
            return False  # environment constrained
        if self.container is None:
            return True
        return self.container.can_add_mass(element.total_mass)

    def can_add_mass(self, added_mass: float) -> bool:
        """
        Checks if a mass can be added within the cargo mass capacity.

        Args:
            added_mass (float): The added mass (kg).

        Returns:
            bool: True, if the mass can be added.
        """
        return not (
            self.cargo_mass + added_mass - self.max_cargo_mass
            > self.settings.mass_precision / 2
        )

    def add(self, element: SimElement) -> bool:
        """
        Adds an element to this carrier, removing it from its prior container.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element was added.
        """
        if self.contains(element):
            return True
        if element is self or self.is_inside(element):
            return False  # an element cannot (recursively) contain itself
        if not self.can_add(element):
            return False
        self._attach(element)
        return True

    def remove(self, element: SimElement) -> bool:
        """
        Removes an element from this carrier.

        Args:
            element (:obj:`SimElement`): The element.

        Returns:
            bool: True, if the element was removed.
        """
        return self._detach(element)

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        mass = super().get_total_mass(class_of_supply)
        for element in self._contents:
            mass += element.get_total_mass(class_of_supply)
        return self.settings.round_mass(mass)

    def satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        super().satisfy_demands(demands, simulator)
        for element in self.contents:
            element.satisfy_demands(demands, simulator)


class SimPropulsionSystem:
    """
    An impulsive propulsion system of a propulsive vehicle which burns fuel
    from a fuel tank (which may be shared with other propulsion systems of
    the same vehicle). A bipropellant system also burns oxidizer from an
    oxidizer tank in a fixed (oxidizer-to-fuel) mixture ratio.
    """

    def __init__(
        self,
        propulsion_type: PropulsionType = PropulsionType.OMS,
        *,
        isp: float = 0.0,
        fuel_tank: Optional[SimResourceTank] = None,
        oxidizer_tank: Optional[SimResourceTank] = None,
        mixture_ratio: Optional[float] = None,
    ):
        #: Propulsion type (fired by burns of the same type).
        self.propulsion_type = PropulsionType(propulsion_type)
        #: Specific impulse (s).
        self.isp = isp or 0.0
        #: Fuel tank.
        self.fuel_tank = fuel_tank
        #: Oxidizer tank (bipropellant systems).
        self.oxidizer_tank = oxidizer_tank
        #: Oxidizer-to-fuel mass ratio (bipropellant systems).
        self.mixture_ratio = mixture_ratio

    @property
    def is_bipropellant(self) -> bool:
        """True, if this system burns oxidizer from a separate tank."""
        return (
            self.oxidizer_tank is not None
            and self.mixture_ratio is not None
            and self.mixture_ratio > 0
        )

    def propellant_split(self) -> List[Tuple[SimResourceTank, float]]:
        """
        Lists the tanks from which this system burns propellant with the
        fraction of the burned propellant mass drawn from each.

        Returns:
            [(:obj:`SimResourceTank`, float)]: The (tank, mass fraction) pairs.
        """
        if self.fuel_tank is None:
            return []
        if not self.is_bipropellant:
            return [(self.fuel_tank, 1.0)]
        ratio = self.mixture_ratio
        return [
            (self.fuel_tank, 1 / (1 + ratio)),
            (self.oxidizer_tank, ratio / (1 + ratio)),
        ]

    def __repr__(self) -> str:
        return f"{self.propulsion_type.value} ({self.isp} s)"


class _FueledCarrier(SimCarrier):
    """
    Base class for a carrier with integral fuel (and oxidizer) tanks.
    """

    @property
    def fuel_tanks(self) -> List[SimResourceTank]:
        """
        The (distinct) integral propellant tanks of this carrier, including
        any oxidizer tanks, with the primary fuel tank first.
        """
        raise NotImplementedError()

    @property
    def fuel_tank(self) -> Optional[SimResourceTank]:
        """The primary integral fuel tank of this carrier."""
        tanks = self.fuel_tanks
        return tanks[0] if tanks else None

    def get_tank(self, selector: TankSelector) -> Optional[SimResourceTank]:
        """
        Gets an integral tank of this carrier.

        Args:
            selector (:obj:`TankSelector`): The tank selector.

        Returns:
            :obj:`SimResourceTank`: The tank, or None if it does not exist.
        """
        raise NotImplementedError()

    def find_tanks(self, resource: SimResource) -> List[SimResourceTank]:
        """
        Lists the integral tanks of this carrier which hold (or are empty
        and can receive) a resource.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            [:obj:`SimResourceTank`]: The tanks, those holding the resource first.
        """
        holding = [t for t in self.fuel_tanks if t.resource == resource]
        empty = [t for t in self.fuel_tanks if t.resource is None]
        return holding + empty

    def _attach_tank(self, tank: SimResourceTank, key: str, role: str = "Fuel"):
        tank.key = key
        tank.role = role
        tank.name = f"{self.name} {key} Tank"
        tank.container = self

    def get_total_mass(self, class_of_supply: Optional[ClassOfSupply] = None) -> float:
        mass = super().get_total_mass(class_of_supply)
        for tank in self.fuel_tanks:
            mass += tank.get_total_mass(class_of_supply)
        return self.settings.round_mass(mass)

    def satisfy_demands(self, demands: DemandSet, simulator: "Simulator"):
        for tank in self.fuel_tanks:
            tank.satisfy_demands(demands, simulator)
        super().satisfy_demands(demands, simulator)


class SimPropulsiveVehicle(_FueledCarrier):
    """
    A carrier with one or more impulsive propulsion systems which can
    traverse space edges.
    """

    element_type = ElementType.PROPULSIVE_VEHICLE

    def __init__(
        self,
        settings: Settings,
        *,
        propulsion_systems: Optional[List[SimPropulsionSystem]] = None,
        **kwargs,
    ):
        super().__init__(settings, **kwargs)
        #: Propulsion systems (with distinct propulsion types).
        self.propulsion_systems: List[SimPropulsionSystem] = list(
            propulsion_systems or []
        )
        for system in self.propulsion_systems:
            label = system.propulsion_type.value
            for tank, role in (
                (system.fuel_tank, "Fuel"),
                (system.oxidizer_tank, "Oxidizer"),
            ):
                if tank is not None and tank.container is not self:
                    self._attach_tank(tank, f"{label} {role}", role)

    @property
    def fuel_tanks(self) -> List[SimResourceTank]:
        tanks: List[SimResourceTank] = []
        for system in self.propulsion_systems:
            for tank in (system.fuel_tank, system.oxidizer_tank):
                if tank is not None and not any(tank is t for t in tanks):
                    tanks.append(tank)
        return tanks

    def get_tank(self, selector: TankSelector) -> Optional[SimResourceTank]:
        selector = TankSelector(selector)
        system = self.get_propulsion_system(selector.propulsion_type)
        if system is None:
            return None
        return system.oxidizer_tank if selector.is_oxidizer else system.fuel_tank

    def get_propulsion_system(
        self, propulsion_type: PropulsionType
    ) -> Optional[SimPropulsionSystem]:
        """
        Gets the propulsion system of a type.

        Args:
            propulsion_type (:obj:`PropulsionType`): The propulsion type.

        Returns:
            :obj:`SimPropulsionSystem`: The propulsion system (None if this
            vehicle has no propulsion system of the type).
        """
        for system in self.propulsion_systems:
            if system.propulsion_type == propulsion_type:
                return system
        return None


class SimSurfaceVehicle(_FueledCarrier):
    """
    A carrier with a fuel tank which can traverse surface edges.
    """

    element_type = ElementType.SURFACE_VEHICLE

    def __init__(
        self,
        settings: Settings,
        *,
        max_speed: float = 0.0,
        fuel_tank: Optional[SimResourceTank] = None,
        **kwargs,
    ):
        super().__init__(settings, **kwargs)
        self._fuel_tank = (
            fuel_tank if fuel_tank is not None else SimResourceTank(settings)
        )
        self._attach_tank(self._fuel_tank, "Fuel")
        #: Maximum speed (km/hr).
        self.max_speed = max_speed or 0.0

    @property
    def fuel_tanks(self) -> List[SimResourceTank]:
        return [self._fuel_tank]

    def get_tank(self, selector: TankSelector) -> Optional[SimResourceTank]:
        return None if TankSelector(selector).is_oxidizer else self._fuel_tank
