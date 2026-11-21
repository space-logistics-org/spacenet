"""
Object schemas for the results of a full simulation.
"""

from typing import Dict, List, Optional
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ...schemas import Scenario
from ..records import ElementSnapshot
from ..simulator import FullSimulator
from .issues import SimIssue, collect_issues
from .missions import LocationSummary
from .propellant import PropellantAnalysis
from .state import ElementState


class MeasureTotals(CamelModel):
    """
    Total measures of effectiveness of a scenario.
    """

    crew_surface_days: float = Field(0.0, description="Crew surface days (crew-days)")
    crew_time: float = Field(0.0, description="Crew time (crew-hours)")
    exploration_capability: float = Field(
        0.0, description="Exploration capability (kg-crew-days)"
    )
    exploration_mass_delivered: float = Field(
        0.0, description="Exploration mass delivered (kg)"
    )
    launch_mass: float = Field(0.0, description="Mass (kg) launched from Earth")
    up_mass_capacity_utilization: float = Field(
        0.0, description="Fraction of cargo capacity used by transports from Earth"
    )
    down_mass_capacity_utilization: float = Field(
        0.0, description="Fraction of cargo capacity used by transports to Earth"
    )
    relative_exploration_capability: float = Field(
        0.0,
        description="Exploration capability per launch mass relative to Apollo 17",
    )
    propellant_burned_mass: float = Field(
        0.0, description="Propellant mass (kg) burned by vehicles"
    )
    propellant_boiloff_mass: float = Field(
        0.0, description="Propellant mass (kg) lost to boiloff"
    )
    propellant_transfer_loss_mass: float = Field(
        0.0, description="Propellant mass (kg) lost in transfers"
    )


class MeasureRecord(CamelModel):
    """
    One record of a measure of effectiveness.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    location: Optional[UUID] = Field(None, description="Location unique identifier")
    amount: float = Field(0.0, description="Amount of the measure")
    type: Optional[str] = Field(None, description="Category (crew time)")
    capacity: Optional[float] = Field(
        None, description="Capacity (kg) (capacity utilization)"
    )


def _records(history, amount=lambda m: m.amount) -> List[MeasureRecord]:
    return [
        MeasureRecord(
            time=m.time,
            location=None if m.location is None else m.location.id,
            amount=amount(m),
            type=getattr(m, "type", None),
            capacity=getattr(m, "capacity", None),
        )
        for m in history
    ]


class Measures(CamelModel):
    """
    Histories of the measures of effectiveness of a scenario.
    """

    crew_surface_days: List[MeasureRecord] = []
    crew_time: List[MeasureRecord] = []
    exploration_capability: List[MeasureRecord] = []
    exploration_mass_delivered: List[MeasureRecord] = []
    launch_mass: List[MeasureRecord] = []
    up_mass_capacity_utilization: List[MeasureRecord] = []
    down_mass_capacity_utilization: List[MeasureRecord] = []


class NetworkState(CamelModel):
    """
    Elements at each network location at a point in time.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    locations: Dict[UUID, List[ElementState]] = Field(
        {}, description="Top-level elements by location unique identifier"
    )


class MassSeries(CamelModel):
    """
    Mass of one class of supply over time.
    """

    class_of_supply: int = Field(..., description="Top-level class of supply")
    points: List[List[float]] = Field(
        [], description="Pairs of time (days) and mass (kg)"
    )


class MassHistory(CamelModel):
    """
    Mass by class of supply of a location or an element over time.
    """

    id: UUID = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name")
    type: Optional[str] = Field(None, description="Element type")
    series: List[MassSeries] = Field([], description="Mass by class of supply")


def _add_point(history: Dict[int, List[List[float]]], times: int, masses: Dict):
    """Adds the masses at one time, padding classes of supply first seen later."""
    for class_of_supply in set(history) | set(masses):
        points = history.setdefault(class_of_supply, [0.0] * times)
        points.append(masses.get(class_of_supply, 0.0))


def _to_series(times: List[float], history: Dict[int, List[float]]) -> List[MassSeries]:
    return [
        MassSeries(
            class_of_supply=class_of_supply,
            points=[[t, m] for t, m in zip(times, masses)],
        )
        for class_of_supply, masses in sorted(history.items())
    ]


class SimulationAnalysis(CamelModel):
    """
    Results of a full simulation of a scenario.
    """

    issues: List[SimIssue] = Field([], description="Errors and warnings")
    error_count: int = Field(0, description="Number of events which failed")
    unsatisfied_demand_count: int = Field(
        0, description="Number of demands which could not be satisfied"
    )
    end_time: float = Field(0.0, description="Time (days) of the last event")
    totals: MeasureTotals = Field(
        MeasureTotals(), description="Total measures of effectiveness"
    )
    measures: Measures = Field(
        Measures(), description="Histories of the measures of effectiveness"
    )
    locations: List[LocationSummary] = Field([], description="Network locations")
    network_history: List[NetworkState] = Field(
        [], description="Elements at each location at each time step"
    )
    location_history: List[MassHistory] = Field(
        [], description="Mass by class of supply at each location over time"
    )
    element_history: List[MassHistory] = Field(
        [], description="Mass by class of supply of each element over time"
    )
    propellant: PropellantAnalysis = Field(
        PropellantAnalysis(), description="Vehicle tank contents and budgets"
    )

    @classmethod
    def create(
        cls, scenario: Scenario, simulator: Optional[FullSimulator] = None
    ) -> "SimulationAnalysis":
        """
        Executes a full simulation of a scenario (including its manifest).

        Args:
            scenario (:obj:`Scenario`): The scenario.
            simulator (:obj:`FullSimulator`): An executed simulator to
                report (default: a new simulator is executed).

        Returns:
            :obj:`SimulationAnalysis`: The analysis results.
        """
        # pylint: disable=too-many-locals
        if simulator is None:
            simulator = FullSimulator(scenario)
            simulator.simulate()
        network = simulator.state.network
        times = [s.time for s in simulator.network_history]
        location_masses: Dict[UUID, Dict[int, List[float]]] = {
            l.id: {} for l in network.locations
        }
        element_masses: Dict[UUID, Dict[int, List[float]]] = {}
        element_info: Dict[UUID, ElementSnapshot] = {}

        def visit(snapshot: ElementSnapshot, index: int, seen: set):
            seen.add(snapshot.id)
            element_info[snapshot.id] = snapshot
            history = element_masses.setdefault(snapshot.id, {})
            # pad the time steps before the element existed
            for points in history.values():
                points.extend([0.0] * (index - len(points)))
            _add_point(history, index, snapshot.mass_by_class_of_supply)
            for child in snapshot.contents:
                visit(child, index, seen)

        network_history = []
        for index, snapshot in enumerate(simulator.network_history):
            seen: set = set()
            for location_id, elements in snapshot.locations.items():
                masses: Dict[int, float] = {}
                for element in elements:
                    visit(element, index, seen)
                    for key, mass in element.mass_by_class_of_supply.items():
                        masses[key] = masses.get(key, 0.0) + mass
                _add_point(location_masses.setdefault(location_id, {}), index, masses)
            network_history.append(
                NetworkState(
                    time=snapshot.time,
                    locations={
                        location_id: [ElementState.from_snapshot(e) for e in elements]
                        for location_id, elements in snapshot.locations.items()
                    },
                )
            )
        # pad the time steps after an element was removed
        for history in element_masses.values():
            for points in history.values():
                points.extend([0.0] * (len(times) - len(points)))
        propellant = PropellantAnalysis.create(simulator)

        return cls(
            issues=collect_issues(simulator),
            error_count=len(simulator.spatial_errors),
            unsatisfied_demand_count=len(simulator.unsatisfied_demands),
            end_time=simulator.time,
            totals=MeasureTotals(
                crew_surface_days=simulator.total_crew_surface_days,
                crew_time=simulator.total_crew_time,
                exploration_capability=simulator.total_exploration_capability,
                exploration_mass_delivered=simulator.total_exploration_mass_delivered,
                launch_mass=simulator.total_launch_mass,
                up_mass_capacity_utilization=simulator.total_up_mass_capacity_utilization,
                down_mass_capacity_utilization=simulator.total_down_mass_capacity_utilization,
                relative_exploration_capability=simulator.total_relative_exploration_capability,
                propellant_burned_mass=propellant.totals.burned_mass,
                propellant_boiloff_mass=propellant.totals.boiloff_mass,
                propellant_transfer_loss_mass=propellant.totals.transfer_loss_mass,
            ),
            propellant=propellant,
            measures=Measures(
                crew_surface_days=_records(simulator.crew_surface_days_history),
                crew_time=_records(simulator.crew_time_history),
                exploration_capability=_records(
                    simulator.exploration_capability_history,
                    lambda m: m.mass * m.duration,
                ),
                exploration_mass_delivered=_records(
                    simulator.exploration_mass_delivered_history
                ),
                launch_mass=_records(simulator.launch_mass_history),
                up_mass_capacity_utilization=_records(
                    simulator.up_mass_capacity_utilization_history
                ),
                down_mass_capacity_utilization=_records(
                    simulator.down_mass_capacity_utilization_history
                ),
            ),
            locations=[LocationSummary(id=n.id, name=n.name) for n in network.nodes]
            + [
                LocationSummary(id=e.id, name=e.name, is_edge=True)
                for e in network.edges
            ],
            network_history=network_history,
            location_history=[
                MassHistory(
                    id=l.id,
                    name=l.name,
                    series=_to_series(times, location_masses.get(l.id, {})),
                )
                for l in network.locations
            ],
            element_history=[
                MassHistory(
                    id=element_id,
                    name=element_info[element_id].name,
                    type=element_info[element_id].type,
                    series=_to_series(times, history),
                )
                for element_id, history in sorted(
                    element_masses.items(), key=lambda i: element_info[i[0]].name
                )
            ],
        )
