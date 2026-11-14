"""
Resources and demands used during simulation.
"""

from typing import Dict, Iterable, Iterator, List, Optional
from uuid import UUID

from ..schemas import AllResources, ClassOfSupply, Environment, ResourceType
from .settings import Settings

_ENVIRONMENT_ORDER = {Environment.PRESSURIZED: 0, Environment.UNPRESSURIZED: 1}

# volume (m^3) per kg of a generic resource, checked in order
_GENERIC_UNIT_VOLUME = (
    (ClassOfSupply.COS_1, 1900 / 1e6),
    (ClassOfSupply.COS_201, 1 / 1e3),
    (ClassOfSupply.COS_2, 7000 / 1e6),
    (ClassOfSupply.COS_3, 5000 / 1e6),
    (ClassOfSupply.COS_4, 3000 / 1e6),
    (ClassOfSupply.COS_5, 7000 / 1e6),
    (ClassOfSupply.COS_6, 5000 / 1e6),
    (ClassOfSupply.COS_7, 5000 / 1e6),
    (ClassOfSupply.COS_8, 3500 / 1e6),
    (ClassOfSupply.COS_9, 3500 / 1e6),
    (ClassOfSupply.COS_10, 7000 / 1e6),
)


class SimResource:
    """
    A resource type that can be demanded, stored, produced, or consumed.

    Resources are either specific (defined in the scenario resource list and
    identified by a unique identifier) or generic (identified by a class of
    supply and environment with a unit mass of 1 kg).
    """

    def __init__(
        self,
        settings: Settings,
        *,
        name: str,
        class_of_supply: ClassOfSupply,
        environment: Environment = Environment.UNPRESSURIZED,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
        units: str = "kg",
        unit_mass: float = 1.0,
        unit_volume: float = 0.0,
        packing_factor: float = 0.0,
        discrete: bool = False,
        index: int = 0,
    ):
        self.settings = settings
        self.id = id
        self.name = name
        self.description = description
        self.class_of_supply = ClassOfSupply(class_of_supply)
        self.environment = Environment(environment)
        self.units = units
        self.unit_mass = unit_mass
        self._unit_volume = unit_volume
        self._packing_factor = packing_factor
        self.discrete = discrete
        self.index = index

    @classmethod
    def from_schema(
        cls, settings: Settings, resource: AllResources, index: int = 0
    ) -> "SimResource":
        """
        Creates a specific resource from its schema.

        Args:
            settings (:obj:`Settings`): The simulation settings.
            resource (:obj:`AllResources`): The resource schema.
            index (int): The position in the scenario resource list.

        Returns:
            :obj:`SimResource`: The simulation resource.
        """
        return cls(
            settings,
            id=resource.id,
            name=resource.name,
            description=resource.description,
            class_of_supply=resource.class_of_supply,
            environment=resource.environment,
            units=resource.units,
            unit_mass=resource.unit_mass,
            unit_volume=resource.unit_volume,
            packing_factor=resource.packing_factor,
            discrete=resource.type == ResourceType.DISCRETE,
            index=index,
        )

    @classmethod
    def generic(
        cls,
        settings: Settings,
        class_of_supply: ClassOfSupply,
        environment: Environment = Environment.UNPRESSURIZED,
    ) -> "SimResource":
        """
        Creates a generic resource for a class of supply.

        Args:
            settings (:obj:`Settings`): The simulation settings.
            class_of_supply (:obj:`ClassOfSupply`): The class of supply.
            environment (:obj:`Environment`): The stowage environment.

        Returns:
            :obj:`SimResource`: The simulation resource.
        """
        class_of_supply = ClassOfSupply(class_of_supply)
        return cls(
            settings,
            name=f"Generic COS {int(class_of_supply)} ({class_of_supply.get_name()})",
            class_of_supply=class_of_supply,
            environment=environment,
        )

    @property
    def is_generic(self) -> bool:
        """True, if this resource is identified only by its class of supply."""
        return self.id is None

    @property
    def is_item(self) -> bool:
        """True, if this resource is demanded in discrete (whole unit) amounts."""
        return self.discrete

    @property
    def resource_type(self) -> str:
        """The resource type label (Generic, Continuous, or Discrete)."""
        if self.is_generic:
            return "Generic"
        return (
            ResourceType.DISCRETE.value
            if self.discrete
            else ResourceType.CONTINUOUS.value
        )

    @property
    def unit_volume(self) -> float:
        """The volume (m^3) of one unit."""
        if self.is_generic:
            for class_of_supply, unit_volume in _GENERIC_UNIT_VOLUME:
                if self.class_of_supply.is_instance_of(class_of_supply):
                    return unit_volume
        return self._unit_volume

    @property
    def packing_factor(self) -> float:
        """The mass (kg) of packing material (COS 5) required per unit."""
        if self.is_generic:
            if self.class_of_supply == ClassOfSupply.COS_203:
                return self.settings.generic_packing_factor_gas
            if self.class_of_supply == ClassOfSupply.COS_201:
                return self.settings.generic_packing_factor_liquid
            if self.environment == Environment.UNPRESSURIZED:
                return self.settings.generic_packing_factor_unpressurized
            return self.settings.generic_packing_factor_pressurized
        return self._packing_factor

    @property
    def key(self) -> tuple:
        """The hashable key which establishes resource equality."""
        if self.is_generic:
            return ("generic", int(self.class_of_supply), self.environment.value)
        return ("specific", self.id, self.environment.value)

    @property
    def sort_key(self) -> tuple:
        """The key which establishes resource ordering."""
        return (
            int(self.class_of_supply),
            0 if self.is_generic else 1,
            self.index,
            _ENVIRONMENT_ORDER[self.environment],
        )

    def is_substitutable_for(self, resource: "SimResource") -> bool:
        """
        Checks if this resource can be substituted for another resource. A
        generic resource can substitute for any resource with the same or a
        more general class of supply and a specific resource can only
        substitute for itself.

        Args:
            resource (:obj:`SimResource`): The resource to be substituted.

        Returns:
            bool: True, if this resource is a valid substitute.
        """
        if resource is None:
            return False
        if self.is_generic:
            return self.class_of_supply.is_instance_of(resource.class_of_supply)
        return self.id == resource.id

    def __eq__(self, other):
        return isinstance(other, SimResource) and self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"SimResource({self.name!r})"


class Demand:
    """
    An amount of a resource. Positive amounts represent consumption and
    negative amounts represent production.
    """

    def __init__(self, resource: Optional[SimResource] = None, amount: float = 0.0):
        self.resource = resource
        self._amount = amount

    @property
    def amount(self) -> float:
        """The demanded amount (units) rounded to the demand precision."""
        if self.resource is None:
            return self._amount
        return self.resource.settings.round_demand(self._amount)

    @amount.setter
    def amount(self, amount: float):
        self._amount = amount

    @property
    def raw_amount(self) -> float:
        """The demanded amount (units) without rounding."""
        return self._amount

    @property
    def mass(self) -> float:
        """The demanded mass (kg) rounded to the mass precision."""
        if self.resource is None:
            return 0.0
        return self.resource.settings.round_mass(self.resource.unit_mass * self._amount)

    @property
    def volume(self) -> float:
        """The demanded volume (m^3) rounded to the volume precision."""
        if self.resource is None:
            return 0.0
        return self.resource.settings.round_volume(
            self.resource.unit_volume * self._amount
        )

    def copy(self) -> "Demand":
        """Creates a copy of this demand."""
        return Demand(self.resource, self._amount)

    def __str__(self):
        if self.resource is None:
            return f"{self.amount:.2f} units of unknown"
        return f"{self.amount:.2f} {self.resource.units} of {self.resource.name}"

    def __repr__(self):
        return f"Demand({self})"


class DemandSet:
    """
    A set of demands which aggregates amounts of equal resources.
    """

    def __init__(self, demands: Optional[Iterable[Demand]] = None):
        self._demands: Dict[tuple, Demand] = {}
        if demands is not None:
            self.add_all(demands)

    def add(self, demand: Demand) -> bool:
        """
        Adds a demand to this set, aggregating with any existing demand for
        the same resource. The demand object itself is never retained.

        Args:
            demand (:obj:`Demand`): The demand to add.

        Returns:
            bool: True, if the demand was added.
        """
        if demand is None or demand.resource is None:
            return False
        existing = self._demands.get(demand.resource.key)
        if existing is not None:
            existing.amount = existing.amount + demand.amount
        else:
            self._demands[demand.resource.key] = Demand(demand.resource, demand.amount)
        return True

    def add_all(self, demands: Iterable[Demand]):
        """
        Adds several demands to this set.

        Args:
            demands (:obj:`Iterable[Demand]`): The demands to add.
        """
        for demand in list(demands):
            self.add(demand)

    def remove(self, demand: Demand) -> bool:
        """
        Removes a demanded amount from this set. If this set contains at
        least the demanded amount, the argument is reduced to zero, otherwise
        it is reduced by the amount contained in this set.

        Args:
            demand (:obj:`Demand`): The demand to remove.

        Returns:
            bool: True, if the entire demanded amount was removed.
        """
        if demand is None or demand.resource is None:
            return False
        existing = self._demands.get(demand.resource.key)
        if existing is None:
            return False
        if existing.amount >= demand.amount:
            amount = demand.amount
            demand.amount = 0
            existing.amount = existing.amount - amount
            return True
        demand.amount = demand.amount - existing.amount
        existing.amount = 0
        return False

    def get(self, resource: SimResource) -> Optional[Demand]:
        """
        Gets the demand for a resource.

        Args:
            resource (:obj:`SimResource`): The resource.

        Returns:
            :obj:`Demand`: The demand, or `None` if not in this set.
        """
        return self._demands.get(resource.key)

    @property
    def total_mass(self) -> float:
        """The total mass (kg) of all demands."""
        if not self._demands:
            return 0.0
        settings = next(iter(self._demands.values())).resource.settings
        return settings.round_mass(sum(d.mass for d in self._demands.values()))

    @property
    def total_volume(self) -> float:
        """The total volume (m^3) of all demands."""
        if not self._demands:
            return 0.0
        settings = next(iter(self._demands.values())).resource.settings
        return settings.round_volume(sum(d.volume for d in self._demands.values()))

    def clear(self):
        """Removes all demands from this set."""
        self._demands.clear()

    def clean(self):
        """Removes all demands with zero amount from this set."""
        for key in [k for k, d in self._demands.items() if d.amount == 0]:
            del self._demands[key]

    def copy(self) -> "DemandSet":
        """Creates a copy of this demand set."""
        return DemandSet(self)

    def to_list(self) -> List[Demand]:
        """Lists the demands in resource order."""
        return sorted(self._demands.values(), key=lambda d: d.resource.sort_key)

    def __iter__(self) -> Iterator[Demand]:
        return iter(self.to_list())

    def __len__(self):
        return len(self._demands)

    def __str__(self):
        return "[" + ", ".join(str(d) for d in self) + "]"

    def __repr__(self):
        return f"DemandSet({self})"
