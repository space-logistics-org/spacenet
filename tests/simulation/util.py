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

    def vehicle(
        self, name="Stage", mass=1000, fuel=9000, isp=300, max_cargo_mass=0, **kwargs
    ):
        """Adds a propulsive vehicle."""
        template = s.PropulsiveVehicle(
            name=name,
            mass=mass,
            max_cargo_mass=max_cargo_mass,
            max_crew=kwargs.pop("max_crew", 0),
            isp=isp,
            max_fuel=kwargs.pop("max_fuel", fuel),
            fuel=s.ResourceAmount(resource=self.fuel.id, amount=fuel),
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
            max_fuel=100,
            fuel=s.ResourceAmount(resource=self.fuel.id, amount=100),
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
            scenario_type="Lunar",
            network=s.Network(
                nodes=[self.ksc, self.leo, self.lsp, self.lsp2],
                edges=[self.ksc_leo, self.ksc_lsp, self.lsp_ksc, self.lsp_lsp2],
            ),
            mission_list=self.missions,
            element_templates=self.templates,
            instantiated_elements=self.instances,
            demand_models=self.demand_models,
            resource_list=[self.water, self.fuel, self.spare],
            configuration=self.configuration,
        )
