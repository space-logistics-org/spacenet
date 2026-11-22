"""
Utilities to build small scenarios for simulation tests.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from spacenet import schemas as s

START = datetime(2030, 1, 1, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[2]


def load_scenario(path: str) -> s.Scenario:
    """Loads a scenario from a file relative to the project root."""
    with open(ROOT / path, encoding="utf-8") as scenario_file:
        return s.Scenario.model_validate_json(scenario_file.read())


class ScenarioBuilder:
    """
    Builds a scenario with a small Earth-Moon network:

     * KSC (Earth surface), LEO (Earth orbit), LSP and LSP2 (Moon surface)
     * KSC-LEO space edge (6 hours, one 1000 m/s burn at departure)
     * KSC-LSP flight edge (3 days, 2 crew, 10000 kg)
     * LSP-KSC flight edge (3 days, 2 crew, 5000 kg)
     * LSP-LSP2 surface edge (86.4 km)
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, **configuration):
        self.ksc = s.SurfaceNode(
            name="KSC", body_1="Earth", latitude=28.6, longitude=-80.6
        )
        self.leo = s.OrbitalNode(
            name="LEO", body_1="Earth", apoapsis=300, periapsis=300, inclination=28.5
        )
        self.lsp = s.SurfaceNode(name="LSP", body_1="Moon", latitude=-89.9, longitude=0)
        self.lsp2 = s.SurfaceNode(name="LSP2", body_1="Moon", latitude=-89, longitude=0)
        self.burn = s.Burn(time=timedelta(0), delta_v=1000)
        self.rcs_burn = s.Burn(time=timedelta(hours=3), delta_v=10, type="RCS")
        self.ksc_leo = s.SpaceEdge(
            name="KSC-LEO",
            origin=self.ksc.id,
            destination=self.leo.id,
            duration=timedelta(hours=6),
            burns=[self.burn],
        )
        self.ksc_lsp = s.FlightEdge(
            name="KSC-LSP",
            origin=self.ksc.id,
            destination=self.lsp.id,
            duration=timedelta(days=3),
            max_crew=2,
            max_cargo=10000,
        )
        self.lsp_ksc = s.FlightEdge(
            name="LSP-KSC",
            origin=self.lsp.id,
            destination=self.ksc.id,
            duration=timedelta(days=3),
            max_crew=2,
            max_cargo=5000,
        )
        self.lsp_lsp2 = s.SurfaceEdge(
            name="LSP-LSP2",
            origin=self.lsp.id,
            destination=self.lsp2.id,
            distance=86400,
        )
        self.water = s.ContinuousResource(
            name="Water",
            class_of_supply=201,
            environment="Unpressurized",
            packing_factor=0.5,
            unit_mass=1,
            unit_volume=0.001,
        )
        self.fuel = s.ContinuousResource(
            name="Fuel",
            class_of_supply=101,
            environment="Unpressurized",
            packing_factor=0,
            unit_mass=1,
            unit_volume=0,
        )
        self.oxidizer = s.ContinuousResource(
            name="Oxidizer",
            class_of_supply=101,
            environment="Unpressurized",
            packing_factor=0,
            unit_mass=1,
            unit_volume=0,
        )
        self.spare = s.DiscreteResource(
            name="Spare",
            class_of_supply=4011,
            environment="Unpressurized",
            packing_factor=0,
            unit_mass=5,
            unit_volume=0,
        )
        self.templates = []
        self.instances = []
        self.demand_models = []
        self.missions = []
        self.configuration = s.Configuration(**configuration)
        #: Date of the scenario end (default: the last event).
        self.end_date = None

    def add(self, template, cls, name=None, **overrides):
        """Adds an element template (once) and an instance of it."""
        if template not in self.templates:
            self.templates.append(template)
        instance = cls(name=name or template.name, template_id=template.id, **overrides)
        self.instances.append(instance)
        return instance

    def element(self, name="Element", **kwargs):
        """Adds a generic element."""
        return self.add(s.Element(name=name, **kwargs), s.InstElement)

    def carrier(
        self, name="Carrier", mass=1000, max_cargo_mass=5000, max_crew=2, **kwargs
    ):
        """Adds an element carrier."""
        template = s.ElementCarrier(
            name=name,
            mass=mass,
            max_cargo_mass=max_cargo_mass,
            max_crew=max_crew,
            **kwargs,
        )
        return self.add(template, s.InstElementCarrier)

    def crew(self, name="Crew", mass=100, active_time_fraction=0.5, **kwargs):
        """Adds a crew member."""
        template = s.HumanAgent(
            name=name, mass=mass, active_time_fraction=active_time_fraction, **kwargs
        )
        return self.add(template, s.InstHumanAgent)

    def container(
        self, name="Tank", mass=10, max_cargo_mass=100, contents=None, **kwargs
    ):
        """Adds a resource container."""
        template = s.ResourceContainer(
            name=name,
            mass=mass,
            max_cargo_mass=max_cargo_mass,
            contents=contents or [],
            **kwargs,
        )
        return self.add(template, s.InstResourceContainer)

    def tank(self, amount, max_amount=None, resource=None, boiloff_rate=None):
        """Creates a fuel (or other resource) tank."""
        return s.ResourceTank(
            max_amount=amount if max_amount is None else max_amount,
            contents=s.ResourceAmount(
                resource=(resource or self.fuel).id, amount=amount
            ),
            boiloff_rate=boiloff_rate,
        )

    def biprop_vehicle(
        self,
        name="Lander",
        mass=1000,
        fuel=2000,
        oxidizer=6000,
        mixture_ratio=3.0,
        isp=350,
        boiloff_rate=None,
        **kwargs,
    ):
        """
        Adds a propulsive vehicle with a bipropellant orbital maneuvering
        system with separate fuel and oxidizer tanks.
        """
        system = s.PropulsionSystem(
            type="OMS",
            isp=isp,
            mixture_ratio=mixture_ratio,
            fuel_tank=self.tank(
                fuel, kwargs.pop("max_fuel", None), boiloff_rate=boiloff_rate
            ),
            oxidizer_tank=self.tank(
                oxidizer,
                kwargs.pop("max_oxidizer", None),
                resource=self.oxidizer,
                boiloff_rate=boiloff_rate,
            ),
        )
        template = s.PropulsiveVehicle(
            name=name,
            mass=mass,
            max_cargo_mass=kwargs.pop("max_cargo_mass", 0),
            max_crew=kwargs.pop("max_crew", 0),
            propulsion_systems=[system, *kwargs.pop("extra_systems", [])],
            **kwargs,
        )
        return self.add(template, s.InstPropulsiveVehicle)

    def transfer(self, origin, destination, location, days=0, priority=1, **kwargs):
        """Makes an event to transfer resources between containers."""
        return s.TransferResources(
            name="Transfer",
            priority=priority,
            mission_time=timedelta(days=days),
            location=location.id,
            origin_container=origin.id,
            destination_container=destination.id,
            **kwargs,
        )

    def burn_event(self, elements, burn=None, location=None, days=0, priority=1):
        """Makes a propulsive burn event in which each element burns in turn."""
        return s.PropulsiveBurn(
            name="Burn",
            priority=priority,
            mission_time=timedelta(days=days),
            location=(location or self.leo).id,
            elements=[e.id for e in elements],
            burn=(burn or self.burn).id,
            burn_stage_sequence=[
                s.BurnStageItem(type="Burn", element=e.id) for e in elements
            ],
        )

    def vehicle(
        self, name="Stage", mass=1000, fuel=9000, isp=300, max_cargo_mass=0, **kwargs
    ):
        """
        Adds a propulsive vehicle with an orbital maneuvering system and,
        if `rcs_isp` is defined, a reaction control system which has its own
        fuel tank (`rcs_fuel`) or otherwise shares the fuel tank of the
        orbital maneuvering system.
        """
        systems = [
            s.PropulsionSystem(
                type="OMS",
                isp=isp,
                fuel_tank=self.tank(fuel, kwargs.pop("max_fuel", None)),
            )
        ]
        rcs_isp = kwargs.pop("rcs_isp", None)
        rcs_fuel = kwargs.pop("rcs_fuel", None)
        if rcs_isp is not None and rcs_fuel is not None:
            systems.append(
                s.PropulsionSystem(
                    type="RCS", isp=rcs_isp, fuel_tank=self.tank(rcs_fuel)
                )
            )
        elif rcs_isp is not None:
            systems.append(
                s.PropulsionSystem(type="RCS", isp=rcs_isp, shared_fuel_tank="OMS")
            )
        template = s.PropulsiveVehicle(
            name=name,
            mass=mass,
            max_cargo_mass=max_cargo_mass,
            max_crew=kwargs.pop("max_crew", 0),
            propulsion_systems=systems,
            **kwargs,
        )
        return self.add(template, s.InstPropulsiveVehicle)

    def rover(self, name="Rover", mass=500, **kwargs):
        """Adds a surface vehicle."""
        template = s.SurfaceVehicle(
            name=name,
            mass=mass,
            max_cargo_mass=kwargs.pop("max_cargo_mass", 1000),
            max_crew=kwargs.pop("max_crew", 2),
            max_speed=10,
            fuel_tank=self.tank(100),
            **kwargs,
        )
        return self.add(template, s.InstSurfaceVehicle)

    def mission(self, events, name="Mission", days=0, demand_models=None, **kwargs):
        """Adds a mission starting a number of days after the scenario start."""
        mission = s.Mission(
            name=name,
            start_date=START + timedelta(days=days),
            events=events,
            demand_models=demand_models or [],
            origin=kwargs.pop("origin", self.ksc.id),
            destination=kwargs.pop("destination", self.lsp.id),
            **kwargs,
        )
        self.missions.append(mission)
        return mission

    def create(self, elements, container, location=None, days=0, priority=1):
        """Makes an event to create elements in a node or carrier."""
        return s.CreateElements(
            name="Create",
            priority=priority,
            mission_time=timedelta(days=days),
            location=(location or container).id,
            container=container.id,
            elements=[e.id for e in elements],
        )

    def move(self, elements, container, location, days=0, priority=1):
        """Makes an event to move elements to a node or carrier."""
        return s.MoveElements(
            name="Move",
            priority=priority,
            mission_time=timedelta(days=days),
            location=location.id,
            container=container.id,
            elements=[e.id for e in elements],
        )

    def flight(self, elements, edge, days=0, priority=2):
        """Makes an event to transport elements along a flight edge."""
        location = self.ksc if edge is self.ksc_lsp else self.lsp
        return s.FlightTransport(
            name="Flight",
            priority=priority,
            mission_time=timedelta(days=days),
            location=location.id,
            edge=edge.id,
            elements=[e.id for e in elements],
        )

    def build(self) -> s.Scenario:
        """Builds the scenario."""
        return s.Scenario(
            name="Test",
            created_by="Test",
            start_date=START,
            end_date=self.end_date,
            scenario_type="Lunar",
            network=s.Network(
                nodes=[self.ksc, self.leo, self.lsp, self.lsp2],
                edges=[self.ksc_leo, self.ksc_lsp, self.lsp_ksc, self.lsp_lsp2],
            ),
            mission_list=self.missions,
            element_templates=self.templates,
            instantiated_elements=self.instances,
            demand_models=self.demand_models,
            resource_list=[self.water, self.fuel, self.oxidizer, self.spare],
            configuration=self.configuration,
        )
