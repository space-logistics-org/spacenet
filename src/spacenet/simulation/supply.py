"""
Supply network objects used to aggregate demands and analyze repairability.
"""

from typing import TYPE_CHECKING, List

from .records import ElementSnapshot
from .resources import Demand

if TYPE_CHECKING:  # pragma: no cover
    from .elements import SimElement
    from .network import SimEdge, SimNode


class RepairItem:
    """
    A demand for a part of an element which could be repaired rather than replaced.
    """

    def __init__(self, demand: Demand, element: "SimElement"):
        self.demand = demand
        self.element = element

    def _get_part_application(self):
        for application in self.element.parts:
            if application.part == self.demand.resource:
                return application
        return None

    @property
    def unit_mean_repair_time(self) -> float:
        """The mean crew time (hours) to repair one unit."""
        application = self._get_part_application()
        return float("inf") if application is None else application.mean_time_to_repair

    @property
    def mean_repair_time(self) -> float:
        """The mean crew time (hours) to repair the demanded amount."""
        return self.unit_mean_repair_time * self.demand.amount

    @property
    def unit_mass_to_repair(self) -> float:
        """The mass (kg, generic COS 4) required to repair one unit."""
        application = self._get_part_application()
        return 0.0 if application is None else application.mass_to_repair

    @property
    def mass_to_repair(self) -> float:
        """The mass (kg, generic COS 4) required to repair the demanded amount."""
        return self.unit_mass_to_repair * self.demand.amount

    @property
    def repair_value(self) -> float:
        """
        The crew time (hours) required per mass (kg) saved by repairing
        rather than replacing (lower values are more attractive).
        """
        mass_saved = self.demand.resource.unit_mass - self.unit_mass_to_repair
        if mass_saved == 0:
            return float("inf")
        return self.unit_mean_repair_time / mass_saved

    def copy(self) -> "RepairItem":
        """Creates a copy of this repair item with an independent demand."""
        return RepairItem(self.demand.copy(), self.element)

    def __str__(self):
        return f"{self.demand} ({self.mass_to_repair:.3f} kg, {self.mean_repair_time:.3f} hr)"

    def __repr__(self):
        return f"RepairItem({self})"


class SupplyEdge:
    """
    A transport along an edge which can supply resources to its destination.
    """

    def __init__(
        self,
        edge: "SimEdge",
        is_reversed: bool,
        start_time: float,
        end_time: float,
        carriers: List[ElementSnapshot],
    ):
        self.edge = edge
        self.is_reversed = is_reversed
        #: Time (days) at which the transport departs.
        self.start_time = start_time
        #: Time (days) at which the transport arrives.
        self.end_time = end_time
        #: Snapshots of the transported carriers at the time of departure.
        self.carriers = carriers
        self.point = SupplyPoint(self)

    @property
    def origin(self) -> "SimNode":
        """The node from which the transport departs."""
        return self.edge.destination if self.is_reversed else self.edge.origin

    @property
    def destination(self) -> "SimNode":
        """The node at which the transport arrives."""
        return self.edge.origin if self.is_reversed else self.edge.destination

    @property
    def all_carriers(self) -> List[ElementSnapshot]:
        """The transported carriers including (recursively) nested carriers."""
        carriers = []
        for carrier in self.carriers:
            carriers.extend(carrier.all_carriers)
        return carriers

    @property
    def max_cargo_mass(self) -> float:
        """The cargo mass capacity (kg) of the transport."""
        if self.edge.is_flight:
            return self.edge.max_cargo_mass
        return sum(c.max_cargo_mass for c in self.carriers)

    @property
    def net_cargo_mass(self) -> float:
        """The unused cargo mass capacity (kg) of the transport."""
        if self.edge.is_flight:
            return self.max_cargo_mass - sum(c.total_mass for c in self.carriers)
        return self.max_cargo_mass - sum(c.cargo_mass for c in self.carriers)

    @property
    def max_cargo_volume(self) -> float:
        """The cargo volume capacity (m^3) of the transport."""
        return sum(c.max_cargo_volume for c in self.carriers)

    @property
    def net_cargo_volume(self) -> float:
        """The unused cargo volume capacity (m^3) of the transport."""
        return sum(c.max_cargo_volume - c.cargo_volume for c in self.carriers)

    def __str__(self):
        return (
            f"{self.origin} ({self.start_time:.1f}) - "
            f"{self.destination} ({self.end_time:.1f})"
        )

    def __repr__(self):
        return f"SupplyEdge({self})"


class SupplyPoint:
    """
    The arrival of a transport at a node at which resources can be supplied.
    """

    def __init__(self, edge: SupplyEdge):
        self.edge = edge

    @property
    def node(self) -> "SimNode":
        """The node at which resources are supplied."""
        return self.edge.destination

    @property
    def time(self) -> float:
        """The time (days) at which resources are supplied."""
        return self.edge.end_time

    def __str__(self):
        return f"{self.node} ({self.time:.1f})"

    def __repr__(self):
        return f"SupplyPoint({self})"
