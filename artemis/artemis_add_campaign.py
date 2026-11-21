"""
Generates a reference Artemis campaign scenario following the program of
record in NASA's Moon-to-Mars Architecture Definition Document (ADD):

* Artemis I: uncrewed SLS Block 1 / Orion mission to lunar orbit.
* Artemis II: crewed lunar free-return flyby.
* Gateway: Power and Propulsion Element (PPE) and Habitation and Logistics
  Outpost (HALO) co-launched on a commercial launch vehicle to NRHO.
* Artemis III: crewed landing at the lunar south pole with a Starship-class
  Human Landing System (HLS) refueled in low Earth orbit from a propellant
  depot filled by a campaign of tanker flights.
* Artemis IV and V: crewed landings via Gateway with SLS Block 1B, which
  co-manifests the International Habitation Module (I-Hab) and the ESPRIT
  refueling and communications module, respectively.

All values are notional or approximate public values intended to exercise
the propellant logistics analysis rather than to reproduce a specific
design. They can be changed with :class:`CampaignParameters` or by editing
the scenario.

=====================================  ==============  ==========================
Value                                  Default         Basis
=====================================  ==============  ==========================
HLS dry mass                           100,000 kg      notional (Starship-class)
HLS propellant capacity                1,200,000 kg    notional (Starship-class)
HLS / tanker / depot specific impulse  375 s           approx. Raptor vacuum
LOX/LCH4 mixture ratio                 3.6             approx. Raptor
HLS residual propellant after launch   50,000 kg       notional
Tanker propellant delivery             150,000 kg      public estimates 100-150 t
Depot propellant capacity              1,500,000 kg    notional
Depot boiloff                          0.05 %/day      notional passive LEO depot
HLS boiloff                            0.1 %/day       notional
Transfer loss                          1 %             notional
Tanker flight interval                 6 days          notional launch cadence
SLS / Orion masses and delta-v         see artemis_campaign.py (SciTech 2024)
EUS dry / propellant mass              15,000 / 129,000 kg  approx. public values
PPE / HALO / I-Hab / ESPRIT mass       6,000 / 8,000 / 10,000 / 6,000 kg  notional
Site illumination / longest night      85 % / 100 h    notional (connecting ridge)
HLS load / solar / storage             10 / 30 kW      400 kWh, notional
Fission Surface Power                  40 kWe          6,000 kg, FSP project goal
LTV mass / traverse energy / storage   1,600 kg        0.6 kWh/km, 60 kWh, notional
=====================================  ==============  ==========================

Usage: ``python artemis/artemis_add_campaign.py`` writes
``artemis/artemis_add_campaign.json``.
"""

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from spacenet import schemas as s
from spacenet.simulation import TankerSizingRequest, size_tankers

OMS = s.PropulsionType.OMS
UNPRESSURIZED = "Unpressurized"
PRESSURIZED = "Pressurized"


#: Mean radius (km) of the Moon.
MOON_RADIUS = 1737.4


def _utc(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


def surface_distance(a: s.SurfaceNode, b: s.SurfaceNode) -> float:
    """Gets the great-circle distance (m) between two lunar surface nodes."""
    lat_a, lat_b = math.radians(a.latitude), math.radians(b.latitude)
    delta_lon = math.radians(b.longitude - a.longitude)
    angle = math.acos(
        min(
            1.0,
            math.sin(lat_a) * math.sin(lat_b)
            + math.cos(lat_a) * math.cos(lat_b) * math.cos(delta_lon),
        )
    )
    return MOON_RADIUS * 1000 * angle


@dataclass
class CampaignParameters:
    """Parameters of the reference Artemis campaign."""

    #: Number of tanker flights per landing (None to size with the depot model).
    tanker_count: Optional[int] = None
    #: Propellant mass (kg) offloaded by each tanker flight.
    tanker_delivery: float = 150_000.0
    #: Propellant capacity (kg) of the depot.
    depot_capacity: float = 1_500_000.0
    #: Fraction of the depot capacity lost to boiloff per day.
    depot_boiloff_rate: float = 0.0005
    #: Fraction of the HLS capacity lost to boiloff per day.
    hls_boiloff_rate: float = 0.001
    #: Fraction of the propellant lost in each transfer.
    transfer_loss: float = 0.01
    #: Time (days) between tanker flights.
    tanker_interval_days: float = 6.0
    #: HLS dry mass (kg).
    hls_dry_mass: float = 100_000.0
    #: HLS propellant capacity (kg).
    hls_capacity: float = 1_200_000.0
    #: HLS propellant (kg) remaining after launch to LEO.
    hls_residual: float = 50_000.0
    #: Specific impulse (s) of the LOX/LCH4 vehicles.
    isp: float = 375.0
    #: Oxidizer-to-fuel mixture ratio of the LOX/LCH4 vehicles.
    mixture_ratio: float = 3.6
    #: Surface stay (days) of each landing.
    surface_days: float = 6.5
    #: Average fraction of time the south pole sites are illuminated.
    site_illumination: float = 0.85
    #: Longest continuous darkness (hours) at the south pole sites.
    site_longest_night: float = 100.0
    #: Start dates of the missions.
    dates: Dict[str, datetime] = field(
        default_factory=lambda: {
            "Artemis I": _utc(2022, 11, 16),
            "Artemis II": _utc(2026, 4, 1),
            "Gateway": _utc(2027, 3, 1),
            "Artemis III": _utc(2027, 4, 1),
            "Artemis IV": _utc(2028, 7, 1),
            "Surface Cargo": _utc(2029, 11, 1),
            "Artemis V": _utc(2030, 3, 1),
        }
    )

    def split(self, mass: float) -> Tuple[float, float]:
        """Splits a propellant mass (kg) into (fuel, oxidizer) masses (whole kg)."""
        fuel = round(mass / (1 + self.mixture_ratio))
        return float(fuel), float(round(mass) - fuel)

    def tankers(self) -> int:
        """Gets the number of tanker flights per landing."""
        if self.tanker_count is not None:
            return self.tanker_count
        # the HLS boils off while it waits half a day in LEO to be refueled
        hls_loss = self.hls_boiloff_rate * self.hls_capacity * 0.5
        required = (self.hls_capacity - self.hls_residual + hls_loss) / (
            1 - self.transfer_loss
        )
        sizing = size_tankers(
            TankerSizingRequest(
                required=required * 1.01,  # 1% margin
                tanker_delivery=self.tanker_delivery,
                depot_capacity=self.depot_capacity,
                boiloff_rate=self.depot_boiloff_rate,
                interval_days=self.tanker_interval_days,
                loiter_days=1.0,
                transfer_loss=self.transfer_loss,
            )
        )
        if not sizing.feasible:
            raise ValueError(f"Tanker campaign is infeasible: {sizing.reason}")
        return max(1, sizing.flights)


class CampaignBuilder:
    """Builds the reference Artemis campaign scenario."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, params: Optional[CampaignParameters] = None):
        self.p = params or CampaignParameters()
        self.templates: List = []
        self.instances: List = []
        self.missions: List[s.Mission] = []
        self.ppe = None
        self.fsp = None
        self.science = None
        self.ltv = None
        self.halo = None
        self._build_network()
        self._build_resources()
        self._build_templates()

    # ------------------------------------------------------------ network

    def _build_network(self):
        self.ksc = s.SurfaceNode(
            name="KSC",
            description="Kennedy Space Center",
            body1="Earth",
            latitude=28.6,
            longitude=-80.6,
        )
        self.pac = s.SurfaceNode(
            name="PAC",
            description="Pacific Ocean Splash-down",
            body1="Earth",
            latitude=32.7,
            longitude=-117.2,
        )
        self.leo = s.OrbitalNode(
            name="LEO",
            description="Low Earth Orbit",
            body1="Earth",
            inclination=28.5,
            periapsis=296.0,
            apoapsis=296.0,
        )
        self.nro = s.LagrangeNode(
            name="NRHO",
            description="Near Rectilinear Halo Orbit (approximated as Earth-Moon L2)",
            body1="Earth",
            body2="Moon",
            lp_number=2,
        )
        self.llo = s.OrbitalNode(
            name="LLO",
            description="Low Lunar Orbit",
            body1="Moon",
            inclination=90.0,
            periapsis=100.0,
            apoapsis=100.0,
        )
        self.lsp = s.SurfaceNode(
            name="LSP",
            description="Lunar South Pole (Shackleton connecting ridge)",
            body1="Moon",
            latitude=-89.4,
            longitude=-137.3,
            illumination=self.p.site_illumination,
            max_night_duration=self.p.site_longest_night,
        )
        self.lsp_2 = s.SurfaceNode(
            name="LSP-2",
            description="Lunar South Pole (Shackleton rim)",
            body1="Moon",
            latitude=-89.8,
            longitude=-150.0,
            illumination=self.p.site_illumination,
            max_night_duration=self.p.site_longest_night,
        )

        def burns(*values):
            return [
                s.Burn(time=timedelta(days=days), delta_v=delta_v)
                for days, delta_v in values
            ]

        self.ksc_leo = s.SpaceEdge(
            name="KSC-LEO (SLS)",
            description="SLS Earth ascent",
            origin=self.ksc.id,
            destination=self.leo.id,
            duration=timedelta(hours=6),
            burns=burns((0, 9500.0)),
        )
        self.leo_nro = s.SpaceEdge(
            name="LEO-NRHO",
            description="Trans-lunar injection and NRHO insertion",
            origin=self.leo.id,
            destination=self.nro.id,
            duration=timedelta(days=7),
            burns=burns(
                (0, 3124.0), (0.3, 30.0), (3.1, 242.0), (4.4, 1.0), (6.4, 126.0)
            ),
        )
        self.leo_pac = s.SpaceEdge(
            name="LEO-PAC (Free Return)",
            description="Lunar free-return flyby",
            origin=self.leo.id,
            destination=self.pac.id,
            duration=timedelta(days=9),
            burns=burns((0, 3124.0), (1.0, 20.0), (5.0, 15.0), (8.5, 10.0)),
        )
        self.nro_llo = s.SpaceEdge(
            name="NRHO-LLO",
            description="Transfer to low lunar orbit",
            origin=self.nro.id,
            destination=self.llo.id,
            duration=timedelta(days=0.5),
            burns=burns((0, 126.4), (0.5, 648.6)),
        )
        self.llo_lsp = s.SpaceEdge(
            name="LLO-LSP",
            description="Lunar descent",
            origin=self.llo.id,
            destination=self.lsp.id,
            duration=timedelta(days=0.2),
            burns=burns((0, 19.4), (0.2, 1692.5)),
        )
        self.lsp_llo = s.SpaceEdge(
            name="LSP-LLO",
            description="Lunar ascent",
            origin=self.lsp.id,
            destination=self.llo.id,
            duration=timedelta(days=0.2),
            burns=burns((0, 1692.4), (0.2, 19.4)),
        )
        self.llo_nro = s.SpaceEdge(
            name="LLO-NRHO",
            description="Transfer to near rectilinear halo orbit",
            origin=self.llo.id,
            destination=self.nro.id,
            duration=timedelta(days=0.5),
            burns=burns((0, 649.2), (0.5, 125.1)),
        )
        self.nro_pac = s.SpaceEdge(
            name="NRHO-PAC",
            description="Trans-Earth injection",
            origin=self.nro.id,
            destination=self.pac.id,
            duration=timedelta(days=6.4),
            burns=burns((0, 147.0), (1.6, 2.0), (2.8, 263.0)),
        )
        self.ksc_leo_ship = s.FlightEdge(
            name="KSC-LEO (Super Heavy)",
            description="Launch of a Starship-class ship (dry mass, residual "
            "propellant, and payload) to LEO",
            origin=self.ksc.id,
            destination=self.leo.id,
            duration=timedelta(days=0.5),
            max_crew=0,
            max_cargo=300_000.0,
        )
        self.leo_ksc_ship = s.FlightEdge(
            name="LEO-KSC (Ship Return)",
            description="Entry and landing of a Starship-class ship for reuse",
            origin=self.leo.id,
            destination=self.ksc.id,
            duration=timedelta(days=0.25),
            max_crew=0,
            max_cargo=300_000.0,
        )
        self.ksc_nro_fh = s.FlightEdge(
            name="KSC-NRHO (Falcon Heavy + SEP)",
            description="Commercial launch and solar electric propulsion "
            "transfer of Gateway elements to NRHO",
            origin=self.ksc.id,
            destination=self.nro.id,
            duration=timedelta(days=365),
            max_crew=0,
            max_cargo=16_000.0,
        )
        self.lsp_lsp_2 = s.SurfaceEdge(
            name="LSP-LSP-2",
            description="Traverse between south pole sites",
            origin=self.lsp.id,
            destination=self.lsp_2.id,
            distance=round(surface_distance(self.lsp, self.lsp_2)),
        )
        self.ksc_lsp_cargo = s.FlightEdge(
            name="KSC-LSP (Cargo Lander)",
            description="Commercial delivery of surface cargo to the south pole",
            origin=self.ksc.id,
            destination=self.lsp.id,
            duration=timedelta(days=6),
            max_crew=0,
            max_cargo=15_000.0,
        )
        self.nodes = [
            self.ksc,
            self.pac,
            self.leo,
            self.nro,
            self.llo,
            self.lsp,
            self.lsp_2,
        ]
        self.edges = [
            self.ksc_leo,
            self.leo_nro,
            self.leo_pac,
            self.nro_llo,
            self.llo_lsp,
            self.lsp_llo,
            self.llo_nro,
            self.nro_pac,
            self.ksc_leo_ship,
            self.leo_ksc_ship,
            self.ksc_nro_fh,
            self.lsp_lsp_2,
            self.ksc_lsp_cargo,
        ]

    # ---------------------------------------------------------- resources

    def _build_resources(self):
        def propellant(name, description, cos, density):
            return s.ContinuousResource(
                name=name,
                description=description,
                class_of_supply=cos,
                environment=UNPRESSURIZED,
                units="kg",
                unit_mass=1.0,
                unit_volume=1 / density,
                packing_factor=0.0,
            )

        self.pban = propellant("PBAN Solid", "Solid rocket propellant", 105, 1715)
        self.lox_lh2 = propellant(
            "LOX/LH2", "Liquid oxygen/liquid hydrogen (combined)", 101, 360
        )
        self.mmh_n2o4 = propellant("MMH/N2O4", "Hypergolic propellants", 102, 1200)
        self.lox = propellant("LOX", "Liquid oxygen", 101, 1141)
        self.lch4 = propellant("LCH4", "Liquid methane", 101, 423)
        self.resources = [self.pban, self.lox_lh2, self.mmh_n2o4, self.lox, self.lch4]
        self.consumables = s.CrewConsumablesDemandModel(
            name="Crew Consumables",
            description="Crew consumables (food, water, gases, hygiene, clothing)",
            reserves_duration=3.0,
            water_recovery_rate=0.0,
            clothing_lifetime=4.0,
            transit_demands_omitted=False,
        )

    # ---------------------------------------------------------- templates

    def _template(self, template):
        self.templates.append(template)
        return template

    def _tank(self, resource, capacity, amount=None, boiloff_rate=None):
        return s.ResourceTank(
            max_amount=capacity,
            contents=s.ResourceAmount(
                resource=resource.id, amount=capacity if amount is None else amount
            ),
            boiloff_rate=boiloff_rate,
        )

    def _stage(self, name, description, mass, cos, resource, capacity, isp, **kwargs):
        return self._template(
            s.PropulsiveVehicle(
                name=name,
                description=description,
                mass=mass,
                class_of_supply=cos,
                environment=UNPRESSURIZED,
                cargo_environment=kwargs.pop("cargo_environment", UNPRESSURIZED),
                max_cargo_mass=kwargs.pop("max_cargo_mass", 0.0),
                max_crew=kwargs.pop("max_crew", 0),
                propulsion_systems=[
                    s.PropulsionSystem(
                        type=OMS, isp=isp, fuel_tank=self._tank(resource, capacity)
                    )
                ],
                **kwargs,
            )
        )

    def _ship(
        self, name, description, mass, capacity, residual, boiloff_rate, **kwargs
    ):
        """A LOX/LCH4 bipropellant ship (HLS, tanker, or depot)."""
        fuel_capacity, oxidizer_capacity = self.p.split(capacity)
        fuel, oxidizer = self.p.split(residual)
        return self._template(
            s.PropulsiveVehicle(
                name=name,
                description=description,
                mass=mass,
                class_of_supply=kwargs.pop("class_of_supply", 9),
                environment=UNPRESSURIZED,
                cargo_environment=kwargs.pop("cargo_environment", UNPRESSURIZED),
                max_cargo_mass=kwargs.pop("max_cargo_mass", 0.0),
                max_crew=kwargs.pop("max_crew", 0),
                propulsion_systems=[
                    s.PropulsionSystem(
                        type=OMS,
                        isp=self.p.isp,
                        mixture_ratio=self.p.mixture_ratio,
                        fuel_tank=self._tank(
                            self.lch4, fuel_capacity, fuel, boiloff_rate
                        ),
                        oxidizer_tank=self._tank(
                            self.lox, oxidizer_capacity, oxidizer, boiloff_rate
                        ),
                    )
                ],
                **kwargs,
            )
        )

    def _module(self, name, description, mass, **kwargs):
        return self._template(
            s.ElementCarrier(
                name=name,
                description=description,
                mass=mass,
                class_of_supply=kwargs.pop("class_of_supply", 9),
                environment=UNPRESSURIZED,
                cargo_environment=PRESSURIZED,
                max_cargo_mass=kwargs.pop("max_cargo_mass", 1000.0),
                max_crew=kwargs.pop("max_crew", 4),
                **kwargs,
            )
        )

    def _build_templates(self):
        p = self.p
        self.t_srbs = self._stage(
            "SLS SRBs",
            "SLS Solid Rocket Boosters (2)",
            195_000.0,
            9021,
            self.pban,
            1_256_000.0,
            269.0,
        )
        self.t_core = self._stage(
            "SLS Core",
            "SLS Core Stage",
            88_275.0,
            9021,
            self.lox_lh2,
            987_000.0,
            414.0,
        )
        self.t_icps = self._stage(
            "iCPS",
            "SLS Interim Cryogenic Propulsion Stage (Block 1)",
            3_490.0,
            9022,
            self.lox_lh2,
            28_576.0,
            465.0,
        )
        self.t_eus = self._stage(
            "EUS",
            "SLS Exploration Upper Stage (Block 1B)",
            15_000.0,
            9022,
            self.lox_lh2,
            129_000.0,
            462.0,
        )
        self.t_sa = self._template(
            s.Element(
                name="SLS SA",
                description="SLS Spacecraft Adapter",
                mass=1_900.0,
                class_of_supply=5,
                environment=UNPRESSURIZED,
            )
        )
        self.t_las = self._template(
            s.ElementCarrier(
                name="SLS LAS",
                description="SLS Launch Abort System",
                mass=7_250.0,
                class_of_supply=9021,
                environment=UNPRESSURIZED,
                cargo_environment=UNPRESSURIZED,
                max_cargo_mass=0.0,
                max_crew=0,
            )
        )
        self.t_sm = self._stage(
            "Orion SM",
            "Orion European Service Module",
            6_185.0,
            9022,
            self.mmh_n2o4,
            9_276.0,
            316.0,
        )
        self.t_cm = self._module(
            "Orion CM", "Orion Crew Module", 9_300.0, max_cargo_mass=1_100.0
        )
        self.t_crew = self._template(
            s.HumanAgent(
                name="Crew Member",
                description="Crew Member",
                mass=100.0,
                class_of_supply=0,
                environment=PRESSURIZED,
                active_time_fraction=0.66,
            )
        )
        self.t_samples = self._template(
            s.Element(
                name="Lunar Samples",
                description="Lunar surface samples",
                mass=100.0,
                class_of_supply=6,
                environment=UNPRESSURIZED,
            )
        )
        self.t_hls = self._ship(
            "HLS",
            "Starship-class Human Landing System",
            p.hls_dry_mass,
            p.hls_capacity,
            p.hls_residual,
            p.hls_boiloff_rate,
            class_of_supply=902,
            cargo_environment=PRESSURIZED,
            max_cargo_mass=15_000.0,
            max_crew=4,
            states=[
                s.State(
                    name="Operations",
                    type="Active",
                    power_consumption=10.0,
                    power_generation=30.0,
                    generation_type="Solar",
                )
            ],
            current_state_index=0,
            energy_storage=s.EnergyStorage(capacity=400.0),
        )
        self.t_tanker = self._ship(
            "Tanker",
            "Starship-class propellant tanker",
            100_000.0,
            p.tanker_delivery,
            p.tanker_delivery,
            p.depot_boiloff_rate,
        )
        self.t_depot = self._ship(
            "Depot",
            "Starship-class propellant depot in LEO",
            120_000.0,
            p.depot_capacity,
            0.0,
            p.depot_boiloff_rate,
        )
        self.t_ppe = self._template(
            s.Element(
                name="PPE",
                description="Gateway Power and Propulsion Element",
                mass=6_000.0,
                class_of_supply=9,
                environment=UNPRESSURIZED,
            )
        )
        self.t_halo = self._module(
            "HALO", "Gateway Habitation and Logistics Outpost", 8_000.0
        )
        self.t_ihab = self._module(
            "I-Hab", "Gateway International Habitation Module", 10_000.0
        )
        self.t_esprit = self._template(
            s.Element(
                name="ESPRIT",
                description="Gateway refueling and communications module",
                mass=6_000.0,
                class_of_supply=9,
                environment=UNPRESSURIZED,
            )
        )
        self.t_fsp = self._template(
            s.Element(
                name="FSP",
                description="Fission Surface Power (40 kWe)",
                mass=6_000.0,
                class_of_supply=803,
                environment=UNPRESSURIZED,
                states=[
                    s.State(name="Stowed", type="Dormant"),
                    s.State(name="Operating", type="Active", power_generation=40.0),
                ],
                current_state_index=0,
                grid_connected=True,
            )
        )
        self.t_science = self._template(
            s.Element(
                name="Science Station",
                description="Surface science instruments and communications",
                mass=800.0,
                class_of_supply=601,
                environment=UNPRESSURIZED,
                states=[
                    s.State(name="Stowed", type="Dormant"),
                    s.State(name="Operating", type="Active", power_consumption=3.0),
                ],
                current_state_index=0,
                grid_connected=True,
            )
        )
        self.t_ltv = self._template(
            s.SurfaceVehicle(
                name="LTV",
                description="Lunar Terrain Vehicle (unpressurized, teleoperable)",
                mass=1_600.0,
                class_of_supply=802,
                environment=UNPRESSURIZED,
                cargo_environment=UNPRESSURIZED,
                max_cargo_mass=800.0,
                max_crew=2,
                max_speed=15.0,
                fuel_tank=self._tank(self.lch4, 0.0),
                energy_consumption=0.6,
                states=[
                    s.State(
                        name="Parked",
                        type="Quiescent",
                        power_consumption=0.3,
                        power_generation=1.5,
                        generation_type="Solar",
                    ),
                    s.State(
                        name="Driving",
                        type="Active",
                        power_consumption=1.0,
                        power_generation=1.5,
                        generation_type="Solar",
                    ),
                ],
                current_state_index=0,
                energy_storage=s.EnergyStorage(capacity=60.0),
                grid_connected=True,
            )
        )

    # ---------------------------------------------------------- instances

    def _instance(self, template, prefix: str, suffix: str = ""):
        cls = {
            s.PropulsiveVehicle: s.InstPropulsiveVehicle,
            s.ElementCarrier: s.InstElementCarrier,
            s.HumanAgent: s.InstHumanAgent,
            s.Element: s.InstElement,
            s.SurfaceVehicle: s.InstSurfaceVehicle,
        }[type(template)]
        instance = cls(
            template_id=template.id,
            name=f"{prefix} | {template.name}{' ' + suffix if suffix else ''}",
        )
        self.instances.append(instance)
        return instance

    # ------------------------------------------------------------- events

    @staticmethod
    def _create(name, day, priority, location, container, elements):
        return s.CreateElements(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=location.id,
            container=container.id,
            elements=[e.id for e in elements],
        )

    @staticmethod
    def _move(name, day, priority, location, container, elements):
        return s.MoveElements(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=location.id,
            container=container.id,
            elements=[e.id for e in elements],
        )

    @staticmethod
    def _remove(name, day, priority, location, elements):
        return s.RemoveElements(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=location.id,
            elements=[e.id for e in elements],
        )

    @staticmethod
    def _flight(name, day, priority, edge, elements):
        return s.FlightTransport(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=edge.origin,
            edge=edge.id,
            elements=[e.id for e in elements],
        )

    @staticmethod
    def _space(name, day, priority, edge, elements, actions: Sequence[Sequence]):
        """
        Makes a space transport with one list of (type, element) actions for
        each burn of the edge.
        """
        return s.SpaceTransport(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=edge.origin,
            edge=edge.id,
            elements=[e.id for e in elements],
            burn_stage_sequence=[
                s.BurnStageSequence(
                    burn=burn.id,
                    actions=[
                        s.BurnStageItem(type=kind, element=element.id)
                        for kind, element in burn_actions
                    ],
                )
                for burn, burn_actions in zip(edge.burns, actions)
            ],
        )

    @staticmethod
    def _transfer(name, day, priority, location, origin, destination, mode, loss):
        return s.TransferResources(
            name=name,
            mission_time=timedelta(days=day),
            priority=priority,
            location=location.id,
            origin_container=origin.id,
            destination_container=destination.id,
            transfer_mode=mode,
            loss_fraction=loss or None,
        )

    def _launch_sls(self, prefix, block_1b: bool, payload=(), crewed=True):
        """
        Creates the SLS / Orion stack and crew and launches it to LEO.
        Returns the (events, stack, upper stage, cm, sm, crew).
        """
        srbs = self._instance(self.t_srbs, prefix)
        core = self._instance(self.t_core, prefix)
        upper = self._instance(self.t_eus if block_1b else self.t_icps, prefix)
        sa = self._instance(self.t_sa, prefix)
        las = self._instance(self.t_las, prefix)
        sm = self._instance(self.t_sm, prefix)
        cm = self._instance(self.t_cm, prefix)
        crew = (
            [self._instance(self.t_crew, prefix, x) for x in "ABCD"] if crewed else []
        )
        stack = [srbs, core, sa, upper, cm, sm, las, *payload]
        ascent = [
            ("Burn", srbs),
            ("Stage", srbs),
            ("Stage", las),
            ("Burn", core),
            ("Stage", core),
            ("Stage", sa),
        ]
        if block_1b:
            # the exploration upper stage completes the ascent
            ascent.append(("Burn", upper))
        events = [
            self._create(
                f"{prefix} | Create Launch Stack", 0, 2, self.ksc, self.ksc, stack
            ),
            *(
                [self._create(f"{prefix} | Create Crew", 0, 3, self.ksc, cm, crew)]
                if crewed
                else []
            ),
            self._space(
                f"{prefix} | Earth Ascent",
                0,
                4,
                self.ksc_leo,
                stack,
                [ascent],
            ),
        ]
        return events, [upper, cm, sm, *payload], upper, cm, sm, crew

    def _tli(self, prefix, day, upper, cm, sm, payload=(), edge=None):
        """Trans-lunar injection by the upper stage with Orion corrections."""
        edge = edge or self.leo_nro
        actions = [[("Burn", upper), ("Stage", upper)]]
        actions += [[("Burn", sm)] for _ in edge.burns[1:]]
        return self._space(
            f"{prefix} | Trans-Lunar Injection",
            day,
            1,
            edge,
            [upper, cm, sm, *payload],
            actions,
        )

    def _tei(self, prefix, day, cm, sm):
        """Trans-Earth injection from NRHO to splash-down."""
        actions = [[("Burn", sm)] for _ in self.nro_pac.burns]
        actions[-1].append(("Stage", sm))
        return self._space(
            f"{prefix} | Trans-Earth Injection", day, 2, self.nro_pac, [cm, sm], actions
        )

    # ----------------------------------------------------------- missions

    def _mission(
        self, name, start, origin, destination, events, crewed=False, **kwargs
    ):
        mission = s.Mission(
            name=name,
            start_date=start,
            origin=origin.id,
            destination=destination.id,
            events=events,
            demand_models=(
                [
                    s.InstCrewConsumablesDemandModel(
                        name="Crew Consumables", template_id=self.consumables.id
                    )
                ]
                if crewed
                else []
            ),
            **kwargs,
        )
        self.missions.append(mission)
        return mission

    def artemis_1(self):
        """Uncrewed SLS / Orion mission to lunar orbit and back."""
        prefix = "Artemis I"
        events, _, upper, cm, sm, _ = self._launch_sls(prefix, False, crewed=False)
        events.append(self._tli(prefix, 1, upper, cm, sm))
        events.append(self._tei(prefix, 14, cm, sm))
        self._mission(
            prefix,
            self.p.dates[prefix],
            self.ksc,
            self.nro,
            events,
            return_origin=self.nro.id,
            return_destination=self.pac.id,
        )

    def artemis_2(self):
        """Crewed lunar free-return flyby."""
        prefix = "Artemis II"
        events, _, upper, cm, sm, _ = self._launch_sls(prefix, False)
        events.append(self._tli(prefix, 1, upper, cm, sm, edge=self.leo_pac))
        events[-1].name = f"{prefix} | Trans-Lunar Injection (Free Return)"
        # the service module is staged before entry
        events.append(
            s.RemoveElements(
                name=f"{prefix} | Service Module Separation",
                mission_time=timedelta(days=10),
                priority=1,
                location=self.pac.id,
                elements=[sm.id],
            )
        )
        self._mission(
            prefix, self.p.dates[prefix], self.ksc, self.pac, events, crewed=True
        )

    def _traverse(self, prefix: str, day: float) -> List[s.SurfaceTransport]:
        """A terrain vehicle traverse to the second site and back."""

        def drive(name: str, start: float, origin: s.SurfaceNode):
            return s.SurfaceTransport(
                name=f"{prefix} | {name}",
                mission_time=timedelta(days=start),
                priority=1,
                location=origin.id,
                edge=self.lsp_lsp_2.id,
                vehicle=self.ltv.id,
                transport_state=1,
                speed=2.0,
                duty_cycle=0.5,
            )

        return [
            drive("LTV Traverse to LSP-2", day, self.lsp),
            drive("LTV Return to LSP", day + 1, self.lsp_2),
        ]

    def surface_cargo(self):
        """
        Commercial delivery of surface infrastructure to the south pole: a
        fission power unit and a science station on a power grid, and a
        lunar terrain vehicle which charges from the grid.
        """
        prefix = "Surface Cargo"
        self.fsp = self._instance(self.t_fsp, prefix)
        self.science = self._instance(self.t_science, prefix)
        self.ltv = self._instance(self.t_ltv, prefix)
        cargo = [self.fsp, self.science, self.ltv]
        events = [
            self._create(f"{prefix} | Create Cargo", 0, 1, self.ksc, self.ksc, cargo),
            self._flight(f"{prefix} | Delivery", 0, 2, self.ksc_lsp_cargo, cargo),
            s.ReconfigureElements(
                name=f"{prefix} | Deploy Power and Science",
                mission_time=timedelta(days=6),
                priority=1,
                location=self.lsp.id,
                elements=[self.fsp.id, self.science.id],
                state_type="Active",
            ),
        ]
        self._mission(prefix, self.p.dates[prefix], self.ksc, self.lsp, events)

    def gateway(self):
        """PPE and HALO co-launched to NRHO."""
        prefix = "Gateway"
        self.ppe = self._instance(self.t_ppe, prefix)
        self.halo = self._instance(self.t_halo, prefix)
        events = [
            self._create(
                f"{prefix} | Create PPE and HALO",
                0,
                1,
                self.ksc,
                self.ksc,
                [self.ppe, self.halo],
            ),
            self._flight(
                f"{prefix} | Launch and Transfer",
                0,
                2,
                self.ksc_nro_fh,
                [self.ppe, self.halo],
            ),
        ]
        self._mission(prefix, self.p.dates[prefix], self.ksc, self.nro, events)

    def aggregation(self, prefix: str, start: datetime):
        """
        Launches a depot and tankers which aggregate propellant in LEO, then
        launches and refuels the HLS which transfers to NRHO. Returns the
        HLS and the time (days after the start) at which it arrives in NRHO.
        """
        p = self.p
        name = f"{prefix} Propellant Aggregation"
        depot = self._instance(self.t_depot, prefix)
        hls = self._instance(self.t_hls, prefix)
        events = [
            self._create(f"{name} | Create Depot", 0, 1, self.ksc, self.ksc, [depot]),
            self._flight(f"{name} | Launch Depot", 0, 2, self.ksc_leo_ship, [depot]),
        ]
        day = 1.0
        count = p.tankers()
        for index in range(count):
            day = 1.0 + index * p.tanker_interval_days
            tanker = self._instance(self.t_tanker, prefix, f"{index + 1:02d}")
            label = f"{name} | Tanker {index + 1:02d}"
            events += [
                self._create(f"{label} Create", day, 1, self.ksc, self.ksc, [tanker]),
                self._flight(f"{label} Launch", day, 2, self.ksc_leo_ship, [tanker]),
                self._transfer(
                    f"{label} Offload",
                    day + 1,
                    1,
                    self.leo,
                    tanker,
                    depot,
                    s.TransferMode.EMPTY_ORIGIN,
                    p.transfer_loss,
                ),
                self._flight(
                    f"{label} Return", day + 1, 2, self.leo_ksc_ship, [tanker]
                ),
            ]
        refuel = day + 2
        events += [
            self._create(
                f"{name} | Create HLS", refuel - 1, 3, self.ksc, self.ksc, [hls]
            ),
            self._flight(
                f"{name} | Launch HLS", refuel - 1, 4, self.ksc_leo_ship, [hls]
            ),
            self._transfer(
                f"{name} | Refuel HLS",
                refuel,
                1,
                self.leo,
                depot,
                hls,
                s.TransferMode.FILL_DESTINATION,
                p.transfer_loss,
            ),
            self._space(
                f"{name} | HLS Transfer to NRHO",
                refuel,
                2,
                self.leo_nro,
                [hls],
                [[("Burn", hls)] for _ in self.leo_nro.burns],
            ),
            self._remove(f"{name} | Depot Disposal", refuel, 3, self.leo, [depot]),
        ]
        self._mission(name, start, self.ksc, self.nro, events)
        return hls, refuel + self.leo_nro.duration.total_seconds() / 86400

    def landing(self, prefix: str, block_1b: bool, payload_template=None):
        """
        A crewed landing: propellant aggregation and HLS transfer to NRHO,
        then an SLS / Orion launch whose crew lands in the HLS.
        """
        start = self.p.dates[prefix]
        hls, hls_arrival = self.aggregation(prefix, start)
        payload = [self._instance(payload_template, prefix)] if payload_template else []
        events, _, upper, cm, sm, crew = self._launch_sls(prefix, block_1b, payload)
        # Orion arrives in NRHO two days after the HLS
        launch = hls_arrival + 2 - 8
        events.append(self._tli(prefix, 1, upper, cm, sm, payload))
        surface = self.p.surface_days
        via_gateway = block_1b
        day = 8
        if via_gateway:
            # the co-manifested module remains at Gateway in NRHO
            events.append(
                self._move(
                    f"{prefix} | Dock at Gateway, Crew to HALO",
                    day,
                    1,
                    self.nro,
                    self.halo,
                    crew[2:],
                )
            )
        samples = self._instance(self.t_samples, prefix)
        events += [
            self._move(
                f"{prefix} | Crew Transfer to HLS", day, 3, self.nro, hls, crew[:2]
            ),
            self._space(
                f"{prefix} | HLS Transfer to LLO",
                day + 1,
                1,
                self.nro_llo,
                [hls],
                [[("Burn", hls)], [("Burn", hls)]],
            ),
            self._space(
                f"{prefix} | Lunar Descent",
                day + 1.5,
                1,
                self.llo_lsp,
                [hls],
                [[("Burn", hls)], [("Burn", hls)]],
            ),
            s.CrewedExploration(
                name=f"{prefix} | Surface Exploration",
                mission_time=timedelta(days=day + 2),
                priority=1,
                location=self.lsp.id,
                vehicle=hls.id,
                duration=timedelta(days=surface),
                eva_per_week=4.0,
                eva_duration=timedelta(hours=8),
                element_states=[
                    s.ElementState(element=c.id, state_index=-1) for c in crew[:2]
                ],
                additional_demands=[],
            ),
            self._create(
                f"{prefix} | Collect Samples",
                day + 2 + surface,
                1,
                self.lsp,
                hls,
                [samples],
            ),
            self._space(
                f"{prefix} | Lunar Ascent",
                day + 2 + surface,
                2,
                self.lsp_llo,
                [hls],
                [[("Burn", hls)], [("Burn", hls)]],
            ),
            self._space(
                f"{prefix} | HLS Transfer to NRHO",
                day + 3 + surface,
                1,
                self.llo_nro,
                [hls],
                [[("Burn", hls)], [("Burn", hls)]],
            ),
            self._move(
                f"{prefix} | Crew and Samples to Orion",
                day + 4 + surface,
                1,
                self.nro,
                cm,
                [*crew[:2], samples] + (crew[2:] if via_gateway else []),
            ),
            self._remove(
                f"{prefix} | HLS Disposal", day + 4 + surface, 2, self.nro, [hls]
            ),
            self._tei(prefix, day + 5 + surface, cm, sm),
        ]
        if self.ltv is not None:
            # the crew teleoperates the terrain vehicle to another site and back
            index = next(
                i for i, e in enumerate(events) if e.name.endswith("Collect Samples")
            )
            events[index:index] = self._traverse(prefix, day + 3)
        self._mission(
            prefix,
            start + timedelta(days=launch),
            self.ksc,
            self.lsp,
            events,
            crewed=True,
            return_origin=self.lsp.id,
            return_destination=self.pac.id,
        )

    def build(self) -> s.Scenario:
        """Builds the campaign scenario."""
        self.artemis_1()
        self.artemis_2()
        self.gateway()
        self.landing("Artemis III", block_1b=False)
        self.landing("Artemis IV", block_1b=True, payload_template=self.t_ihab)
        self.surface_cargo()
        self.landing("Artemis V", block_1b=True, payload_template=self.t_esprit)
        return s.Scenario(
            name="Artemis Campaign (ADD Baseline)",
            description="Reference Artemis campaign following the program of "
            "record in NASA's Moon-to-Mars Architecture Definition Document, "
            "with propellant aggregation for a Starship-class HLS. Values "
            "are notional (see artemis/artemis_add_campaign.py).",
            created_by="SpaceNet",
            start_date=self.p.dates["Artemis I"],
            scenario_type="Lunar",
            network=s.Network(nodes=self.nodes, edges=self.edges),
            mission_list=sorted(self.missions, key=lambda m: m.start_date),
            resource_list=self.resources,
            element_templates=self.templates,
            instantiated_elements=self.instances,
            demand_models=[self.consumables],
            configuration=s.Configuration(),
        )


def build_scenario(params: Optional[CampaignParameters] = None) -> s.Scenario:
    """
    Builds the reference Artemis campaign scenario.

    Args:
        params (:obj:`CampaignParameters`): The campaign parameters.

    Returns:
        :obj:`Scenario`: The scenario.
    """
    return CampaignBuilder(params).build()


if __name__ == "__main__":
    scenario = build_scenario()
    path = Path(__file__).with_name("artemis_add_campaign.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(scenario.model_dump_json(exclude_none=True, indent=2, by_alias=True))
    print(f"Wrote {path}")
