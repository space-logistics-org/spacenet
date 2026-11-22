"""
Object schemas for the analysis of in-situ resource utilization (ISRU): the
rate, power, and production of each ISRU process over time.
"""

from typing import Dict, List, Optional

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..simulator import Simulator


class ISRUProcessHistory(CamelModel):
    """
    Operation of an ISRU process of an element over time, with one value per
    interval between events.
    """

    key: str = Field(..., description="Process identifier (element and process)")
    element_name: str = Field(..., description="Element name")
    process: str = Field(..., description="Process name")
    location_names: List[Optional[str]] = Field(
        [], description="Location (name) during each interval"
    )
    starts: List[float] = Field([], description="Start time (days) of each interval")
    ends: List[float] = Field([], description="End time (days) of each interval")
    rate: List[float] = Field(
        [], description="Average rate (fraction of the full rate)"
    )
    limit: List[Optional[str]] = Field(
        [], description="Constraint which limits the rate (if any)"
    )
    power: List[float] = Field([], description="Average power consumed (kW)")
    outputs: Dict[str, List[float]] = Field(
        {},
        description="Cumulative mass (kg) of each output at the end of each interval",
    )
    total_inputs: Dict[str, float] = Field(
        {}, description="Mass (kg) of each input consumed"
    )
    total_outputs: Dict[str, float] = Field(
        {}, description="Mass (kg) of each output produced"
    )
    total_energy: float = Field(0.0, description="Energy consumed (kWh)")
    operating_days: float = Field(
        0.0, description="Equivalent duration (days) of operation at the full rate"
    )
    duration: float = Field(0.0, description="Duration (days) in an active state")
    specific_energy: Optional[float] = Field(
        None,
        description="Energy consumed per mass of the first output (kWh/kg)",
    )
    limits: Dict[str, float] = Field(
        {}, description="Duration (days) limited by each constraint"
    )


class ISRUAnalysis(CamelModel):
    """
    Operation of each ISRU process over time.
    """

    processes: List[ISRUProcessHistory] = Field([], description="ISRU processes")
    total_outputs: Dict[str, float] = Field(
        {}, description="Mass (kg) of each resource produced by all processes"
    )
    total_inputs: Dict[str, float] = Field(
        {}, description="Mass (kg) of each resource consumed by all processes"
    )
    total_energy: float = Field(0.0, description="Energy (kWh) consumed")

    @property
    def total_output_mass(self) -> float:
        """The mass (kg) of all resources produced."""
        return sum(self.total_outputs.values())

    @classmethod
    def create(cls, simulator: Simulator) -> "ISRUAnalysis":
        """
        Creates the ISRU analysis of an executed simulator.

        Args:
            simulator (:obj:`Simulator`): The executed simulator.

        Returns:
            :obj:`ISRUAnalysis`: The analysis.
        """
        processes: Dict[str, ISRUProcessHistory] = {}
        first_outputs: Dict[str, str] = {}
        for record in simulator.isru_records:
            key = f"{record.element_id}:{record.process}"
            history = processes.get(key)
            if history is None:
                history = processes[key] = ISRUProcessHistory(
                    key=key, element_name=record.element_name, process=record.process
                )
                history.outputs = {name: [] for name in record.output_masses}
                first_outputs[key] = next(iter(record.output_masses), None)
            history.location_names.append(record.location_name)
            history.starts.append(record.time - record.duration)
            history.ends.append(record.time)
            history.rate.append(record.rate)
            history.limit.append(record.limit)
            history.power.append(record.power)
            for name, mass in record.output_masses.items():
                history.total_outputs[name] = (
                    history.total_outputs.get(name, 0.0) + mass
                )
                history.outputs.setdefault(name, []).append(history.total_outputs[name])
            for name, mass in record.input_masses.items():
                history.total_inputs[name] = history.total_inputs.get(name, 0.0) + mass
            history.total_energy += record.energy
            history.operating_days += record.rate * record.duration
            history.duration += record.duration
            if record.limit is not None:
                history.limits[record.limit] = (
                    history.limits.get(record.limit, 0.0) + record.duration
                )
        totals_out: Dict[str, float] = {}
        totals_in: Dict[str, float] = {}
        for key, history in processes.items():
            first = first_outputs.get(key)
            produced = history.total_outputs.get(first, 0.0) if first else 0.0
            if produced > 0:
                history.specific_energy = history.total_energy / produced
            for name, mass in history.total_outputs.items():
                totals_out[name] = totals_out.get(name, 0.0) + mass
            for name, mass in history.total_inputs.items():
                totals_in[name] = totals_in.get(name, 0.0) + mass
        return cls(
            processes=list(processes.values()),
            total_outputs=totals_out,
            total_inputs=totals_in,
            total_energy=sum(h.total_energy for h in processes.values()),
        )
