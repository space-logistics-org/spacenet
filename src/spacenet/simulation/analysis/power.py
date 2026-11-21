"""
Object schemas for the analysis of electrical power and energy: the energy
balance of each power group (an element with its contents, or the
grid-connected elements at a surface node) over time.
"""

from typing import Dict, List
from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..simulator import Simulator


class PowerGroupHistory(CamelModel):
    """
    Energy balance of a power group (a grid or an element with its contents,
    wherever it is located) over time, with one value per interval between
    events.
    """

    key: str = Field(..., description="Group identifier")
    name: str = Field(..., description="Group name (grid or element)")
    elements: List[str] = Field(
        [], description="Elements which generate, consume, or store power"
    )
    locations: List[UUID] = Field(
        [], description="Location (unique identifier) during each interval"
    )
    location_names: List[str] = Field(
        [], description="Location (name) during each interval"
    )
    starts: List[float] = Field([], description="Start time (days) of each interval")
    ends: List[float] = Field([], description="End time (days) of each interval")
    generation: List[float] = Field([], description="Average power generated (kW)")
    consumption: List[float] = Field([], description="Power consumed (kW)")
    energy: List[float] = Field([], description="Stored energy (kWh) at the end")
    capacity: List[float] = Field([], description="Energy storage capacity (kWh)")
    deficit: List[float] = Field([], description="Energy (kWh) not supplied")
    night_energy: float = Field(
        0.0, description="Largest energy (kWh) required to survive the longest night"
    )
    night_shortfall: bool = Field(
        False,
        description="True, if the group stayed at a location for a synodic day "
        "without the storage to survive the longest night",
    )
    total_generated: float = Field(0.0, description="Energy generated (kWh)")
    total_consumed: float = Field(0.0, description="Energy consumed (kWh)")
    total_deficit: float = Field(0.0, description="Energy not supplied (kWh)")


class PowerAnalysis(CamelModel):
    """
    Energy balance of each power group over time.
    """

    groups: List[PowerGroupHistory] = Field([], description="Power groups")
    total_deficit: float = Field(
        0.0, description="Energy (kWh) not supplied to all groups"
    )

    @classmethod
    def create(cls, simulator: Simulator) -> "PowerAnalysis":
        """
        Creates the power analysis of an executed simulator.

        Args:
            simulator (:obj:`Simulator`): The executed simulator.

        Returns:
            :obj:`PowerAnalysis`: The analysis.
        """
        groups: Dict[str, PowerGroupHistory] = {}
        for record in simulator.power_records:
            group = groups.get(record.key)
            if group is None:
                group = groups[record.key] = PowerGroupHistory(
                    key=record.key, name=record.name
                )
            for element in record.elements:
                if element not in group.elements:
                    group.elements.append(element)
            hours = 24 * record.duration
            group.locations.append(record.location_id)
            group.location_names.append(record.location_name)
            group.starts.append(record.time - record.duration)
            group.ends.append(record.time)
            group.generation.append(record.generation)
            group.consumption.append(record.consumption)
            group.energy.append(record.energy)
            group.capacity.append(record.capacity)
            group.deficit.append(record.deficit)
            group.night_energy = max(group.night_energy, record.night_energy)
            if record.stays_overnight and record.night_energy > record.capacity:
                group.night_shortfall = True
            group.total_generated += record.generation * hours
            group.total_consumed += record.consumption * hours
            group.total_deficit += record.deficit
        return cls(
            groups=list(groups.values()),
            total_deficit=sum(group.total_deficit for group in groups.values()),
        )
