"""
Demand models which generate demands for resources during simulation.
"""

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from ..schemas import ClassOfSupply, DemandModelType, Environment
from .resources import Demand, DemandSet, SimResource
from .settings import Settings

if TYPE_CHECKING:  # pragma: no cover
    from .elements import SimElement
    from .mission import SimMission
    from .simulator import Simulator


class SimDemandModel:
    """
    Base class for a demand model.
    """

    demand_model_type: DemandModelType = None

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
    ):
        #: Unique identifier of the demand model template.
        self.id = id
        self.name = name if name is not None else self.demand_model_type.value
        self.description = description

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        """
        Generates demands over a duration.

        Args:
            duration (float): The duration (days).
            simulator (:obj:`Simulator`): The simulator.

        Returns:
            :obj:`DemandSet`: The generated demands.
        """
        raise NotImplementedError()

    def __str__(self):
        return self.name


class SimTimedImpulseDemandModel(SimDemandModel):
    """
    Demand model which generates a one-time demand the first time it is used.
    """

    demand_model_type = DemandModelType.TIMED_IMPULSE

    def __init__(self, *, demands: Optional[List[Demand]] = None, **kwargs):
        super().__init__(**kwargs)
        self.demands: List[Demand] = list(demands) if demands is not None else []
        self._generated = False

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        if self._generated:
            return DemandSet()
        self._generated = True
        return DemandSet(self.demands)


class SimRatedDemandModel(SimDemandModel):
    """
    Demand model which generates demands at a constant rate.
    """

    demand_model_type = DemandModelType.RATED

    def __init__(self, *, demand_rates: Optional[List[Demand]] = None, **kwargs):
        super().__init__(**kwargs)
        #: Demand rates expressed as an amount (units) per day.
        self.demand_rates: List[Demand] = (
            list(demand_rates) if demand_rates is not None else []
        )

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        demands = DemandSet()
        for rate in self.demand_rates:
            # NOTE: the reference implementation rounds the rate to the demand
            # precision before multiplying which distorts small rates
            demands.add(Demand(rate.resource, rate.raw_amount * duration))
        return demands


class SimSparingByMassDemandModel(SimDemandModel):
    """
    Demand model which generates demands for spare parts as a fraction of the
    mass of an element per year.
    """

    demand_model_type = DemandModelType.SPARING_BY_MASS

    def __init__(
        self,
        element: "SimElement",
        *,
        unpressurized_spares_rate: float = 0.0,
        pressurized_spares_rate: float = 0.0,
        parts_list_enabled: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.element = element
        #: Fraction of element mass demanded per year as unpressurized spares.
        self.unpressurized_spares_rate = unpressurized_spares_rate or 0.0
        #: Fraction of element mass demanded per year as pressurized spares.
        self.pressurized_spares_rate = pressurized_spares_rate or 0.0
        #: True, if the element parts list is used to demand specific parts.
        self.parts_list_enabled = (
            True if parts_list_enabled is None else parts_list_enabled
        )

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        element = self.element
        settings: Settings = element.settings
        demands = DemandSet()
        press_part_mass = 0.0
        unpress_part_mass = 0.0

        def fraction(numerator: float, denominator: float) -> float:
            return numerator / denominator if denominator != 0 else 0.0

        if self.parts_list_enabled:
            for part in element.parts:
                if part.quantity > 0:
                    if part.part.environment == Environment.PRESSURIZED:
                        press_part_mass += part.quantity * part.part.unit_mass
                    else:
                        unpress_part_mass += part.quantity * part.part.unit_mass
            generic_part_mass = max(
                0.0, element.mass - press_part_mass - unpress_part_mass
            )
            for part in element.parts:
                if part.quantity > 0:
                    if part.part.environment == Environment.PRESSURIZED:
                        amount = (
                            duration
                            * self.pressurized_spares_rate
                            / 365
                            * element.mass
                            * fraction(
                                part.quantity, generic_part_mass + press_part_mass
                            )
                        )
                    else:
                        amount = (
                            duration
                            * self.unpressurized_spares_rate
                            / 365
                            * element.mass
                            * fraction(
                                part.quantity, generic_part_mass + unpress_part_mass
                            )
                        )
                    demands.add(Demand(part.part, amount))
        else:
            generic_part_mass = element.mass
        demands.add(
            Demand(
                SimResource.generic(
                    settings, ClassOfSupply.COS_4, Environment.UNPRESSURIZED
                ),
                duration
                * self.unpressurized_spares_rate
                / 365
                * element.mass
                * fraction(generic_part_mass, generic_part_mass + unpress_part_mass),
            )
        )
        demands.add(
            Demand(
                SimResource.generic(
                    settings, ClassOfSupply.COS_4, Environment.PRESSURIZED
                ),
                duration
                * self.pressurized_spares_rate
                / 365
                * element.mass
                * fraction(generic_part_mass, generic_part_mass + press_part_mass),
            )
        )
        return demands


class SimCrewConsumablesDemandModel(SimDemandModel):
    """
    Demand model which generates demands for crew consumables over a mission.
    """

    # pylint: disable=too-many-instance-attributes

    demand_model_type = DemandModelType.CREW_CONSUMABLES

    #: Default rate parameters.
    DEFAULTS = {
        "reserves_duration": 0.0,
        "water_recovery_rate": 0.42,
        "clothing_lifetime": 4.0,
        "transit_demands_omitted": False,
        "water_rate": 3.6,
        "eva_water_rate": 0.6875,
        "food_support_rate": 0.05556,
        "ambient_food_rate": 0.76389,
        "rf_food_rate": 1.61667,
        "oxygen_rate": 3.85714,
        "eva_oxygen_rate": 0.07875,
        "nitrogen_rate": 2.21429,
        "hygiene_rate": 0.27778,
        "hygiene_kit": 1.8,
        "clothing_rate": 2.3,
        "personal_items": 10.0,
        "office_equipment": 5.0,
        "eva_suit": 107.0,
        "eva_lithium_hydroxide": 0.3625,
        "health_equipment": 20.0,
        "health_consumables": 0.1,
        "safety_equipment": 25.0,
        "comm_equipment": 20.0,
        "computer_equipment": 5.0,
        "trash_bag_rate": 0.05,
        "waste_containment_rate": 0.05,
    }

    def __init__(
        self,
        mission: "SimMission",
        *,
        name: Optional[str] = None,
        id: Optional[UUID] = None,  # pylint: disable=redefined-builtin
        description: Optional[str] = None,
        **parameters,
    ):
        super().__init__(name=name, id=id, description=description)
        self.mission = mission
        unknown = set(parameters) - set(self.DEFAULTS)
        if unknown:
            raise TypeError(f"Unknown crew consumables parameters: {sorted(unknown)}")
        values = dict(self.DEFAULTS)
        values.update({k: v for k, v in parameters.items() if v is not None})
        self.reserves_duration = values["reserves_duration"]
        self.water_recovery_rate = max(0.0, min(values["water_recovery_rate"], 1.0))
        self.clothing_lifetime = max(1.0, values["clothing_lifetime"])
        self.transit_demands_omitted = values["transit_demands_omitted"]
        self.water_rate = values["water_rate"]
        self.eva_water_rate = values["eva_water_rate"]
        self.food_support_rate = values["food_support_rate"]
        self.ambient_food_rate = values["ambient_food_rate"]
        self.rf_food_rate = values["rf_food_rate"]
        self.oxygen_rate = values["oxygen_rate"]
        self.eva_oxygen_rate = values["eva_oxygen_rate"]
        self.nitrogen_rate = values["nitrogen_rate"]
        self.hygiene_rate = values["hygiene_rate"]
        self.hygiene_kit = values["hygiene_kit"]
        self.clothing_rate = values["clothing_rate"]
        self.personal_items = values["personal_items"]
        self.office_equipment = values["office_equipment"]
        self.eva_suit = values["eva_suit"]
        self.eva_lithium_hydroxide = values["eva_lithium_hydroxide"]
        self.health_equipment = values["health_equipment"]
        self.health_consumables = values["health_consumables"]
        self.safety_equipment = values["safety_equipment"]
        self.comm_equipment = values["comm_equipment"]
        self.computer_equipment = values["computer_equipment"]
        self.trash_bag_rate = values["trash_bag_rate"]
        self.waste_containment_rate = values["waste_containment_rate"]

    @property
    def mission_crew_size(self) -> int:
        """The number of crew members in the mission."""
        return self.mission.crew_size

    @property
    def mission_eva_crew_time(self) -> float:
        """The crew time (hours) spent on extra-vehicular activity in the mission."""
        return self.mission.eva_crew_time

    @property
    def mission_exploration_duration(self) -> float:
        """The duration (days) spent at the mission destination."""
        return self.mission.destination_duration

    @property
    def mission_transit_duration(self) -> float:
        """The duration (days) spent in transit (0 if transit demands are omitted)."""
        if self.transit_demands_omitted:
            return 0.0
        return self.mission.transit_duration + self.mission.return_transit_duration

    def _demands(self, amounts) -> DemandSet:
        settings = self.mission.settings
        demands = DemandSet()
        for class_of_supply, amount in amounts:
            if amount:
                demands.add(
                    Demand(SimResource.generic(settings, class_of_supply), amount)
                )
        return demands

    def daily_demands(self, crew_days: float) -> DemandSet:
        """
        Generates the demands which accrue with time (water, food, gases,
        hygiene, clothing, and waste) for a number of crew-days.

        Args:
            crew_days (float): The crew-days.

        Returns:
            :obj:`DemandSet`: The demands.
        """
        return self._demands(
            [
                (
                    ClassOfSupply.COS_201,
                    crew_days * self.water_rate * (1 - self.water_recovery_rate),
                ),
                (ClassOfSupply.COS_202, crew_days * self.food_support_rate),
                (ClassOfSupply.COS_202, crew_days * self.ambient_food_rate),
                (ClassOfSupply.COS_202, crew_days * self.rf_food_rate),
                (ClassOfSupply.COS_203, crew_days * self.oxygen_rate),
                (ClassOfSupply.COS_203, crew_days * self.nitrogen_rate),
                (ClassOfSupply.COS_204, crew_days * self.hygiene_rate),
                (
                    ClassOfSupply.COS_205,
                    crew_days * self.clothing_rate / self.clothing_lifetime,
                ),
                (ClassOfSupply.COS_701, crew_days * self.trash_bag_rate),
                (ClassOfSupply.COS_702, crew_days * self.waste_containment_rate),
            ]
        )

    def crew_demands(self, crew: int) -> DemandSet:
        """
        Generates the demands which are carried by each crew member (kits,
        personal items, suits, and equipment) and the reserves of daily
        demands for a number of crew members.

        Args:
            crew (int): The number of crew members.

        Returns:
            :obj:`DemandSet`: The demands.
        """
        demands = self._demands(
            [
                (ClassOfSupply.COS_204, self.hygiene_kit * crew),
                (ClassOfSupply.COS_206, self.personal_items * crew),
                (ClassOfSupply.COS_301, self.office_equipment * crew),
                (ClassOfSupply.COS_302, self.eva_suit * crew),
                (ClassOfSupply.COS_303, self.health_consumables * crew),
                (ClassOfSupply.COS_306, self.computer_equipment * crew),
            ]
        )
        if self.reserves_duration > 0:
            reserves = self.daily_demands(self.reserves_duration * crew)
            # reserves exclude clothing and trash (as in the mission total)
            for demand in reserves:
                if demand.resource.class_of_supply in (
                    ClassOfSupply.COS_205,
                    ClassOfSupply.COS_701,
                ):
                    continue
                demands.add(demand)
        return demands

    def mission_demands(self) -> DemandSet:
        """Generates the demands for equipment shared by the mission crew."""
        return self._demands(
            [
                (ClassOfSupply.COS_303, self.health_equipment),
                (ClassOfSupply.COS_304, self.safety_equipment),
                (ClassOfSupply.COS_305, self.comm_equipment),
            ]
        )

    def eva_demands(self) -> DemandSet:
        """Generates the demands for the extra-vehicular activity of the mission."""
        eva_time = self.mission_eva_crew_time
        return self._demands(
            [
                (ClassOfSupply.COS_201, eva_time * self.eva_water_rate),
                (ClassOfSupply.COS_203, eva_time * self.eva_oxygen_rate),
                (ClassOfSupply.COS_302, self.eva_lithium_hydroxide * eva_time),
            ]
        )

    def generate_demands(self, duration: float, simulator: "Simulator") -> DemandSet:
        settings = self.mission.settings
        crew = self.mission_crew_size
        eva_time = self.mission_eva_crew_time
        days = self.mission_exploration_duration + self.mission_transit_duration
        days_with_reserves = days + self.reserves_duration

        amounts = [
            (
                ClassOfSupply.COS_201,
                days_with_reserves
                * self.water_rate
                * crew
                * (1 - self.water_recovery_rate),
            ),
            (ClassOfSupply.COS_201, eva_time * self.eva_water_rate),
            (ClassOfSupply.COS_202, days_with_reserves * self.food_support_rate * crew),
            (ClassOfSupply.COS_202, days_with_reserves * self.ambient_food_rate * crew),
            (ClassOfSupply.COS_202, days_with_reserves * self.rf_food_rate * crew),
            (ClassOfSupply.COS_203, days_with_reserves * self.oxygen_rate * crew),
            (ClassOfSupply.COS_203, eva_time * self.eva_oxygen_rate),
            (ClassOfSupply.COS_203, days_with_reserves * self.nitrogen_rate * crew),
            (ClassOfSupply.COS_204, days_with_reserves * self.hygiene_rate * crew),
            (ClassOfSupply.COS_204, self.hygiene_kit * crew),
            (
                ClassOfSupply.COS_205,
                days * self.clothing_rate * crew / self.clothing_lifetime,
            ),
            (ClassOfSupply.COS_206, self.personal_items * crew),
            (ClassOfSupply.COS_301, self.office_equipment * crew),
            (ClassOfSupply.COS_302, self.eva_suit * crew),
            (ClassOfSupply.COS_302, self.eva_lithium_hydroxide * eva_time),
            (ClassOfSupply.COS_303, self.health_equipment),
            (ClassOfSupply.COS_303, self.health_consumables * crew),
            (ClassOfSupply.COS_304, self.safety_equipment),
            (ClassOfSupply.COS_305, self.comm_equipment),
            (ClassOfSupply.COS_306, self.computer_equipment * crew),
            (ClassOfSupply.COS_701, days * self.trash_bag_rate * crew),
            (
                ClassOfSupply.COS_702,
                days_with_reserves * self.waste_containment_rate * crew,
            ),
        ]
        demands = DemandSet()
        for class_of_supply, amount in amounts:
            demands.add(Demand(SimResource.generic(settings, class_of_supply), amount))
        return demands
