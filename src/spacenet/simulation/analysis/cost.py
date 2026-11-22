"""
Object schemas for the cost analysis of a simulation: the costs incurred by
creating elements (unit costs) and by transports (e.g., launch services).
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi_camelcase import CamelModel
from pydantic import Field

from ..simulator import Simulator


class CostItem(CamelModel):
    """
    A cost incurred during a simulation.
    """

    time: float = Field(..., description="Time (days) relative to the scenario start")
    year: int = Field(..., description="Calendar year")
    mission: Optional[str] = Field(None, description="Mission name")
    category: str = Field(..., description="Category (Element or Transport)")
    item: str = Field(..., description="Costed element or edge")
    amount: float = Field(..., description="Cost (millions of US dollars)")


class CostAnalysis(CamelModel):
    """
    Costs incurred during a simulation, in millions of (then-year) US dollars.
    """

    items: List[CostItem] = Field([], description="Costs in order of time")
    total: float = Field(0.0, description="Total cost")
    by_mission: Dict[str, float] = Field({}, description="Total cost of each mission")
    by_year: Dict[int, float] = Field({}, description="Total cost of each year")
    by_category: Dict[str, float] = Field({}, description="Total cost of each category")

    @classmethod
    def create(cls, simulator: Simulator, start_date: datetime) -> "CostAnalysis":
        """
        Creates the cost analysis of an executed simulator.

        Args:
            simulator (:obj:`Simulator`): The executed simulator.
            start_date (datetime): The start date of the scenario.

        Returns:
            :obj:`CostAnalysis`: The analysis.
        """
        analysis = cls()
        for record in simulator.cost_records:
            year = (start_date + timedelta(days=record.time)).year
            analysis.items.append(
                CostItem(
                    time=record.time,
                    year=year,
                    mission=record.mission,
                    category=record.category,
                    item=record.item,
                    amount=record.amount,
                )
            )
            analysis.total += record.amount
            mission = record.mission or "(none)"
            analysis.by_mission[mission] = (
                analysis.by_mission.get(mission, 0.0) + record.amount
            )
            analysis.by_year[year] = analysis.by_year.get(year, 0.0) + record.amount
            analysis.by_category[record.category] = (
                analysis.by_category.get(record.category, 0.0) + record.amount
            )
        return analysis
