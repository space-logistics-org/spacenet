"""
Generates random (but reproducible and lint-valid) scenarios to test the
invariants of simulations.

Scenarios use the small Earth-Moon network of :class:`ScenarioBuilder`.
Events are planned using the expected location of each element, so many
succeed, but events may also fail (e.g., over capacity or out of fuel) to
test that invariants hold despite errors.
"""

import random
from datetime import timedelta
from typing import Dict, List

from spacenet import schemas as s

from .util import START, ScenarioBuilder


class ScenarioGenerator:
    """
    Generates a random scenario.

    Args:
        seed (int): The seed of the random number generator.
        closed (bool): True, to generate a closed scenario in which the total
            mass of elements and resources is constant after the elements
            are created: no demands, burns, boiloff, losses, or removals.
        java (bool): True, to generate a scenario which the reference (Java)
            implementation can read and simulates in the same way: without
            the features it lacks (e.g., bipropellant vehicles, boiloff,
            power, transfer options, end dates, time-phased consumables,
            and part failures) or models differently (surface transports
            and nested carriers).
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, seed: int, closed: bool = False, java: bool = False):
        self.rng = random.Random(seed)
        self.closed = closed
        self.java = java
        rng = self.rng
        configuration = {}
        if not closed and not java:
            configuration = {
                "time_phased_consumables": rng.random() < 0.5,
                "environment_constrained": rng.random() < 0.3,
                "volume_constrained": rng.random() < 0.3,
            }
            if rng.random() < 0.5:
                configuration["part_failures"] = rng.choice(["Expected", "Random"])
                configuration["random_seed"] = rng.randrange(1000)
        self.b = ScenarioBuilder(**configuration)
        b = self.b
        #: Expected location (node) of each element (by unique identifier).
        self.where: Dict = {}
        self.carriers: List = []
        self.vehicles: List = []
        self.containers: List = []
        self.crew: List = []
        self.rovers: List = []
        self.others: List = []
        if not closed:
            self.consumables = s.CrewConsumablesDemandModel(name="Consumables")
            self.water_demand = s.RatedDemandModel(
                name="Water",
                demands=[s.ResourceAmountRate(resource=b.water.id, rate=1.0)],
            )
            b.demand_models.extend([self.consumables, self.water_demand])

    # ------------------------------------------------------------- elements

    def uniform(self, low: float, high: float) -> float:
        """Draws a random value (rounded to 0.1)."""
        return round(self.rng.uniform(low, high), 1)

    def water(self, amount: float) -> s.ResourceAmount:
        """Makes an amount of water."""
        return s.ResourceAmount(resource=self.b.water.id, amount=amount)

    def make_elements(self):
        """Adds the element templates and instances of the scenario."""
        rng, b = self.rng, self.b
        for i in range(rng.randint(1, 3)):
            kwargs = {}
            if not self.closed and rng.random() < 0.5:
                kwargs = self.habitat_states()
            self.carriers.append(
                b.carrier(
                    f"Carrier {i}",
                    mass=self.uniform(500, 3000),
                    max_cargo_mass=self.uniform(2000, 10000),
                    max_crew=rng.randint(0, 4),
                    cargo_environment=rng.choice(["Pressurized", "Unpressurized"]),
                    **kwargs,
                )
            )
        for i in range(rng.randint(1, 2)):
            boiloff = None if self.closed or self.java or rng.random() < 0.5 else 0.01
            if self.java or rng.random() < 0.5:
                vehicle = b.vehicle(
                    f"Stage {i}",
                    mass=self.uniform(500, 2000),
                    fuel=self.uniform(1000, 9000),
                    max_fuel=10000,
                    isp=self.uniform(250, 450),
                    max_cargo_mass=self.uniform(0, 3000),
                )
                if boiloff:
                    for system in b.templates[-1].propulsion_systems:
                        system.fuel_tank.boiloff_rate = boiloff
            else:
                vehicle = b.biprop_vehicle(
                    f"Lander {i}",
                    mass=self.uniform(500, 2000),
                    fuel=self.uniform(500, 2000),
                    oxidizer=self.uniform(1500, 6000),
                    max_fuel=2500,
                    max_oxidizer=7500,
                    mixture_ratio=3.0,
                    isp=self.uniform(300, 450),
                    boiloff_rate=boiloff,
                    max_cargo_mass=self.uniform(0, 3000),
                )
            self.vehicles.append(vehicle)
        for i in range(rng.randint(1, 3)):
            capacity = self.uniform(100, 1000)
            self.containers.append(
                b.container(
                    f"Tank {i}",
                    max_cargo_mass=capacity,
                    contents=[self.water(self.uniform(0, capacity))],
                )
            )
        for i in range(rng.randint(0, 4)):
            self.crew.append(b.crew(f"Crew {i}", mass=self.uniform(60, 100)))
        if not self.java and rng.random() < 0.5:
            kwargs = {}
            if not self.closed:
                kwargs = {
                    "fuel_consumption": self.uniform(0, 0.5),
                    "energy_consumption": self.uniform(0, 0.5),
                    "energy_storage": s.EnergyStorage(capacity=100),
                }
            self.rovers.append(b.rover("Rover", mass=self.uniform(200, 800), **kwargs))
        if not self.closed and not self.java and rng.random() < 0.5:
            part = s.Part(
                resource=b.spare.id, mean_time_to_failure=timedelta(hours=2000)
            )
            self.others.append(
                b.element(
                    "Instrument",
                    mass=self.uniform(10, 100),
                    parts=[part],
                    states=[s.State(name="On", type="Active")],
                    current_state_index=0,
                )
            )

    def habitat_states(self) -> dict:
        """Makes the operational states of a habitat with demands and power."""
        demand_models = [
            s.InstRatedDemandModel(name="Water", template_id=self.water_demand.id)
        ]
        if self.java:
            state = s.State(name="Active", type="Active", demand_models=demand_models)
            return {
                "states": [state, s.State(name="Dormant", type="Dormant")],
                "current_state_index": 0,
            }
        state = s.State(
            name="Active",
            type="Active",
            demand_models=demand_models,
            power_consumption=self.uniform(0, 5),
            power_generation=self.uniform(0, 8),
            generation_type=self.rng.choice(["Constant", "Solar"]),
        )
        return {
            "states": [state, s.State(name="Dormant", type="Dormant")],
            "current_state_index": 0,
            "energy_storage": s.EnergyStorage(capacity=self.uniform(10, 200)),
        }

    @property
    def elements(self) -> List:
        """All element instances."""
        return [
            *self.carriers,
            *self.vehicles,
            *self.containers,
            *self.crew,
            *self.rovers,
            *self.others,
        ]

    # --------------------------------------------------------------- events

    def at(self, node) -> List:
        """Lists the elements expected at a node."""
        return [e for e in self.elements if self.where.get(e.id) is node]

    def sample(self, items: List, low: int = 1) -> List:
        """Draws a random subset of a list."""
        if not items:
            return []
        return self.rng.sample(
            items, self.rng.randint(min(low, len(items)), len(items))
        )

    def creation_events(self) -> List:
        """Creates all elements at the scenario start (at KSC or LSP)."""
        b, rng = self.b, self.rng
        events = []
        for node in (b.ksc, b.lsp):
            for element in self.elements:
                if element.id not in self.where and rng.random() < 0.5:
                    self.where[element.id] = node
        for element in self.elements:
            self.where.setdefault(element.id, b.ksc)
        for node in (b.ksc, b.lsp):
            here = self.at(node)
            top = [e for e in here if e not in self.crew]
            if top:
                events.append(b.create(top, node, priority=1))
            # crew members (and some cargo) are created in carriers
            carriers = [c for c in self.carriers if c in here and self.has_crew_room(c)]
            for member in [e for e in here if e in self.crew]:
                if carriers:
                    events.append(
                        b.create([member], rng.choice(carriers), node, priority=2)
                    )
                else:
                    events.append(b.create([member], node, priority=2))
        return events

    def random_event(self, days: float):
        """Makes a random event at a mission time (days)."""
        # pylint: disable=too-many-return-statements,too-many-branches
        # pylint: disable=too-many-locals,too-many-statements
        b, rng = self.b, self.rng
        kinds = ["flight", "move", "transfer"]
        if not self.closed:
            kinds += ["launch", "add", "consume", "reconfigure", "remove"]
        if self.rovers:
            kinds.append("drive")
        if self.crew:
            kinds.append("eva")
        kind = rng.choice(kinds)
        node = rng.choice([b.ksc, b.lsp, b.lsp2])
        here = self.at(node)
        priority = rng.randint(1, 5)
        mission_time = timedelta(days=days)
        if kind == "flight":
            node = rng.choice([b.ksc, b.lsp])
            carriers = [c for c in self.at(node) if c in self.carriers + self.vehicles]
            if not carriers:
                return None
            elements = self.sample(carriers)
            edge = b.ksc_lsp if node is b.ksc else b.lsp_ksc
            destination = b.lsp if node is b.ksc else b.ksc
            for element in elements:
                self.move_with_contents(element, destination)
            event = b.flight(elements, edge, priority=priority)
            event.mission_time = mission_time
            return event
        if kind == "launch":
            vehicles = [v for v in self.at(b.ksc) if v in self.vehicles]
            if not vehicles:
                return None
            vehicle = rng.choice(vehicles)
            self.move_with_contents(vehicle, b.leo)
            return s.SpaceTransport(
                name="Launch",
                priority=priority,
                mission_time=mission_time,
                location=b.ksc.id,
                edge=b.ksc_leo.id,
                elements=[vehicle.id],
                burn_stage_sequence=[
                    s.BurnStageSequence(
                        burn=b.burn.id,
                        actions=[s.BurnStageItem(type="Burn", element=vehicle.id)],
                    )
                ],
            )
        if kind == "move":
            movable = [e for e in here if e not in self.rovers]
            if self.java:
                # flights count nested crew differently (see the parity tests)
                movable = [e for e in movable if e not in self.carriers + self.vehicles]
            targets = [c for c in here if c in self.carriers + self.vehicles]
            if not movable:
                return None
            container = rng.choice(targets + [node])
            elements = [e for e in self.sample(movable) if e is not container]
            if not elements:
                return None
            return b.move(elements, container, node, days=days, priority=priority)
        if kind == "transfer":
            holders = [e for e in here if e in self.containers + self.vehicles]
            if self.java:
                # the reference implementation cannot transfer to vehicle tanks
                holders = [e for e in holders if e in self.containers]
            if len(holders) < 2:
                return None
            origin, destination = rng.sample(holders, 2)
            resource = b.water if origin in self.containers else b.fuel
            if self.closed or self.java:
                mode, loss = "Amount", None
            else:
                mode = rng.choice(["Amount", "Fill Destination", "Empty Origin"])
                loss = rng.choice([None, 0.05])
            return b.transfer(
                origin,
                destination,
                node,
                days=days,
                priority=priority,
                resources=[
                    s.ResourceAmount(resource=resource.id, amount=self.uniform(0, 500))
                ],
                transfer_mode=mode,
                loss_fraction=loss,
            )
        if kind == "add":
            containers = [e for e in here if e in self.containers]
            if not containers:
                return None
            return s.AddResources(
                name="Add",
                priority=priority,
                mission_time=mission_time,
                location=node.id,
                container=rng.choice(containers).id,
                resources=[self.water(self.uniform(0, 300))],
            )
        if kind == "consume":
            containers = [e for e in here if e in self.containers]
            if not containers:
                return None
            return s.ConsumeResources(
                name="Consume",
                priority=priority,
                mission_time=mission_time,
                location=node.id,
                source=rng.choice(containers).id,
                resources=[self.water(self.uniform(-100, 300))],
            )
        if kind == "reconfigure":
            habitats = [e for e in here if e in self.carriers and self.has_states(e)]
            if not habitats:
                return None
            return s.ReconfigureElement(
                name="Reconfigure",
                priority=priority,
                mission_time=mission_time,
                location=node.id,
                element=rng.choice(habitats).id,
                # the reference implementation cannot read a state index of -1
                state_index=rng.choice([0, 1] if self.java else [-1, 0, 1]),
            )
        if kind == "remove":
            removable = [e for e in here if e in self.others + self.containers]
            if not removable:
                return None
            element = rng.choice(removable)
            self.where[element.id] = None
            return s.RemoveElements(
                name="Remove",
                priority=priority,
                mission_time=mission_time,
                location=node.id,
                elements=[element.id],
            )
        if kind == "drive":
            rover = self.rovers[0]
            start = self.where.get(rover.id)
            if start not in (b.lsp, b.lsp2):
                return None
            self.move_with_contents(rover, b.lsp2 if start is b.lsp else b.lsp)
            return s.SurfaceTransport(
                name="Drive",
                priority=priority,
                mission_time=mission_time,
                location=start.id,
                edge=b.lsp_lsp2.id,
                vehicle=rover.id,
                speed=self.uniform(1, 3),
            )
        if kind == "eva":
            habitats = [c for c in here if c in self.carriers]
            crew = [c for c in self.crew if self.where.get(c.id) is node]
            if not habitats or not crew:
                return None
            return s.CrewedEVA(
                name="EVA",
                priority=priority,
                mission_time=mission_time,
                location=node.id,
                eva_duration=timedelta(hours=self.uniform(1, 8)),
                vehicle=rng.choice(habitats).id,
                element_states=[
                    s.ElementState(element=c.id, state_index=-1)
                    for c in self.sample(crew)
                ],
                additional_demands=[],
            )
        return None

    def template(self, element):
        """Gets the template of an element."""
        return next(t for t in self.b.templates if t.id == element.template_id)

    def has_crew_room(self, carrier) -> bool:
        """True, if a carrier can hold crew members."""
        return self.template(carrier).max_crew > 0

    def has_states(self, element) -> bool:
        """True, if the template of an element defines states."""
        return bool(self.template(element).states)

    def move_with_contents(self, element, node):
        """
        Updates the expected location of a transported element and of the
        crew members expected to be inside it (approximately).
        """
        origin = self.where.get(element.id)
        self.where[element.id] = node
        for member in self.crew:
            if self.where.get(member.id) is origin and self.rng.random() < 0.5:
                self.where[member.id] = node

    # ------------------------------------------------------------- scenario

    def generate(self) -> s.Scenario:
        """Generates the scenario."""
        rng, b = self.rng, self.b
        self.make_elements()
        b.mission(self.creation_events(), name="Setup")
        start = 0.0
        for index in range(rng.randint(1, 3)):
            start += self.uniform(1, 30)
            events, days = [], 0.0
            for _ in range(rng.randint(2, 8)):
                days += self.uniform(0, 5)
                event = self.random_event(days)
                if event is not None:
                    event.name = f"{event.name} {len(events)}"
                    events.append(event)
            demand_models = []
            if not self.closed and rng.random() < 0.5:
                demand_models = [
                    s.InstCrewConsumablesDemandModel(
                        name="Consumables", template_id=self.consumables.id
                    )
                ]
            b.mission(
                events,
                name=f"Mission {index}",
                days=start,
                demand_models=demand_models,
            )
        if not self.java and rng.random() < 0.5:
            b.end_date = START + timedelta(days=start + self.uniform(0, 60))
        return b.build()


def random_scenario(seed: int, closed: bool = False, java: bool = False) -> s.Scenario:
    """
    Generates a random scenario.

    Args:
        seed (int): The seed of the random number generator.
        closed (bool): True, for a closed scenario (see :class:`ScenarioGenerator`).
        java (bool): True, for a scenario which the reference implementation
            can simulate (see :class:`ScenarioGenerator`).

    Returns:
        :obj:`Scenario`: The scenario.
    """
    return ScenarioGenerator(seed, closed, java).generate()
