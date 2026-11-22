"""
Tests of the scenario linter, which reports all errors and warnings of a
scenario at once.
"""

import io
import unittest
from contextlib import redirect_stdout
from datetime import timedelta
from uuid import uuid4

from spacenet import schemas as s
from spacenet.lint import Severity, errors, lint_scenario, main
from spacenet.simulation import (
    FullSimulator,
    MissionsAnalysis,
    ScenarioError,
    State,
)
from spacenet.trades import get_value

from .simulation.util import ROOT, START, ScenarioBuilder, load_scenario

REFERENCE_SCENARIOS = (
    "quick_start/completed_quick_start_1_w_db.json",
    "quick_start/completed_quick_start_1_wo_db.json",
    "quick_start/completed_quick_start_2_w_db.json",
    "quick_start/completed_quick_start_3_wo_db.json",
    "artemis/artemis_campaign.json",
    "artemis/artemis_add_campaign.json",
)


def water(amount, builder):
    """Makes an amount of the water resource of a builder."""
    return s.ResourceAmount(resource=builder.water.id, amount=amount)


def codes(builder, severity=None):
    """Lints the scenario of a builder and gets (code, path) of each issue."""
    return [
        (i.code, i.path)
        for i in lint_scenario(builder.build())
        if severity is None or i.severity == severity
    ]


class TestReferenceScenarios(unittest.TestCase):
    def test_reference_scenarios_have_no_issues(self):
        for path in REFERENCE_SCENARIOS:
            self.assertEqual(lint_scenario(load_scenario(path)), [], path)


class TestTimesAndAmounts(unittest.TestCase):
    def test_negative_event_time(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp, days=-30)], days=10)
        (issue,) = lint_scenario(b.build())
        self.assertEqual(issue.severity, Severity.ERROR)
        self.assertEqual(issue.code, "negative-time")
        self.assertEqual(issue.path, "missionList/0/events/0/missionTime")
        self.assertEqual((issue.mission_index, issue.event_index), (0, 0))
        self.assertEqual(
            issue.message, "Event Create is before the start of its mission."
        )

    def test_mission_before_the_scenario_start(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp)], days=-1)
        self.assertEqual(
            codes(b), [("before-scenario-start", "missionList/0/startDate")]
        )

    def test_negative_added_and_transferred_amounts(self):
        b = ScenarioBuilder()
        tank, other = b.container("Tank"), b.container("Other")
        b.mission(
            [
                b.create([tank, other], b.lsp),
                s.AddResources(
                    name="Add",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    container=tank.id,
                    resources=[
                        s.GenericResourceAmount(
                            class_of_supply=201, environment="Unpressurized", amount=-50
                        )
                    ],
                ),
                b.transfer(tank, other, b.lsp, resources=[water(-1, b)]),
            ]
        )
        self.assertEqual(
            codes(b),
            [
                ("negative-amount", "missionList/0/events/1/resources/0/amount"),
                ("negative-amount", "missionList/0/events/2/resources/0/amount"),
            ],
        )

    def test_consumed_amounts_may_be_negative(self):
        # a negative consumption produces resources
        b = ScenarioBuilder()
        tank = b.container("Tank")
        b.mission(
            [
                b.create([tank], b.lsp),
                s.ConsumeResources(
                    name="Produce",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    source=tank.id,
                    resources=[water(-5, b)],
                ),
            ]
        )
        self.assertEqual(codes(b), [])

    def test_negative_and_overfilled_initial_contents(self):
        b = ScenarioBuilder()
        b.container("Tank", max_cargo_mass=100, contents=[water(150, b)])
        b.container("Negative", contents=[water(-1, b)])
        b.vehicle("Stage", fuel=200, max_fuel=100)
        self.assertEqual(
            codes(b),
            [
                ("negative-amount", "elementTemplates/1/contents/0/amount"),
                (
                    "over-capacity",
                    "elementTemplates/2/propulsionSystems/0/fuelTank/contents/amount",
                ),
                ("over-capacity", "instantiatedElements/0/contents"),
            ],
        )

    def test_burns_outside_the_transport(self):
        b = ScenarioBuilder()
        b.ksc_leo.burns.append(s.Burn(time=timedelta(hours=-1), delta_v=1))
        b.ksc_leo.burns.append(s.Burn(time=timedelta(days=1), delta_v=1))
        self.assertEqual(
            codes(b),
            [
                ("negative-time", "network/edges/0/burns/1/time"),
                ("burn-after-arrival", "network/edges/0/burns/2/time"),
            ],
        )


class TestReferences(unittest.TestCase):
    def test_all_unknown_references_are_reported(self):
        b = ScenarioBuilder()
        ghost = uuid4()
        b.mission(
            [
                s.CreateElements(
                    name="Create",
                    priority=1,
                    mission_time=timedelta(0),
                    location=ghost,
                    container=b.lsp.id,
                    elements=[ghost],
                ),
                s.MoveElements(
                    name="Move",
                    priority=1,
                    mission_time=timedelta(days=1),
                    location=b.lsp.id,
                    container=ghost,
                    elements=[],
                ),
            ],
            destination=ghost,
        )
        self.assertEqual(
            codes(b),
            [
                ("unknown-node", "missionList/0/destination"),
                ("unknown-location", "missionList/0/events/0/location"),
                ("unknown-element", "missionList/0/events/0/elements/0"),
                ("unknown-element", "missionList/0/events/1/container"),
            ],
        )
        with self.assertRaises(ScenarioError) as context:
            State(b.build())
        error = context.exception
        # the first error is raised with all errors attached
        self.assertEqual(len(error.issues), 4)
        self.assertEqual((error.mission_index, error.event_index), (0, None))
        self.assertTrue(error.message.endswith("(and 3 more errors)"))

    def test_unknown_templates_resources_and_demand_models(self):
        b = ScenarioBuilder()
        element = b.element("Orphan")
        element.template_id = uuid4()
        model = s.InstRatedDemandModel(
            name="Missing",
            template_id=uuid4(),
            demands=[s.ResourceAmountRate(resource=uuid4(), rate=1)],
        )
        b.carrier(
            "Habitat",
            parts=[s.Part(resource=uuid4())],
            states=[s.State(name="On", type="Active", demand_models=[model])],
        )
        b.mission(
            [b.create([element], b.lsp)],
            demand_models=[
                s.InstCrewConsumablesDemandModel(name="Crew", template_id=uuid4())
            ],
        )
        self.assertEqual(
            codes(b),
            [
                ("unknown-resource", "elementTemplates/1/parts/0/resource"),
                (
                    "unknown-demand-model",
                    "elementTemplates/1/states/0/demandModels/0/templateId",
                ),
                (
                    "unknown-resource",
                    "elementTemplates/1/states/0/demandModels/0/demands/0/resource",
                ),
                ("unknown-template", "instantiatedElements/0/templateId"),
                ("unknown-demand-model", "missionList/0/demandModels/0/templateId"),
            ],
        )

    def test_demand_model_type_mismatch(self):
        b = ScenarioBuilder()
        rated = s.RatedDemandModel(name="Rated", demands=[])
        b.demand_models.append(rated)
        b.carrier(
            "Habitat",
            states=[
                s.State(
                    name="On",
                    type="Active",
                    demand_models=[
                        s.InstTimedImpulseDemandModel(name="X", template_id=rated.id)
                    ],
                )
            ],
        )
        ((code, path),) = codes(b)
        self.assertEqual(code, "demand-model-type-mismatch")
        self.assertEqual(path, "elementTemplates/0/states/0/demandModels/0/type")

    def test_state_indexes(self):
        b = ScenarioBuilder()
        element = b.element("Element", states=[s.State(name="On", type="Active")])
        element.current_state_index = 1
        rover = b.rover("Rover")
        b.mission(
            [
                b.create([element, rover], b.lsp),
                s.ReconfigureElement(
                    name="Reconfigure",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    element=element.id,
                    state_index=2,
                ),
                s.SurfaceTransport(
                    name="Drive",
                    priority=3,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    edge=b.lsp_lsp2.id,
                    vehicle=rover.id,
                    transport_state=0,
                    speed=1,
                ),
            ]
        )
        self.assertEqual(
            codes(b),
            [
                ("invalid-state-index", "instantiatedElements/0/currentStateIndex"),
                ("invalid-state-index", "missionList/0/events/1/stateIndex"),
                ("invalid-state-index", "missionList/0/events/2/transportState"),
            ],
        )

    def test_element_and_edge_types(self):
        b = ScenarioBuilder()
        crate = b.container("Crate")
        box = b.element("Box")
        b.mission(
            [
                b.create([crate, box], b.lsp),
                b.move([box], crate, b.lsp),
                s.SurfaceTransport(
                    name="Drive",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    edge=b.ksc_lsp.id,
                    vehicle=box.id,
                    speed=1,
                ),
                s.CrewedEVA(
                    name="EVA",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.lsp.id,
                    eva_duration=timedelta(hours=4),
                    vehicle=box.id,
                    element_states=[],
                    additional_demands=[],
                ),
            ]
        )
        self.assertEqual(
            codes(b),
            [
                ("wrong-element-type", "missionList/0/events/1/container"),
                ("wrong-edge-type", "missionList/0/events/2/edge"),
                ("wrong-element-type", "missionList/0/events/2/vehicle"),
                ("wrong-element-type", "missionList/0/events/3/vehicle"),
            ],
        )

    def test_burns(self):
        b = ScenarioBuilder()
        stage, box = b.vehicle("Stage"), b.element("Box")
        burn = b.burn_event([stage, box])
        burn.burn = uuid4()
        b.mission(
            [
                b.create([stage, box], b.ksc),
                s.SpaceTransport(
                    name="Launch",
                    priority=2,
                    mission_time=timedelta(0),
                    location=b.ksc.id,
                    edge=b.ksc_leo.id,
                    elements=[stage.id],
                    burn_stage_sequence=[
                        s.BurnStageSequence(burn=b.rcs_burn.id, actions=[])
                    ],
                ),
                burn,
            ]
        )
        self.assertEqual(
            codes(b),
            [
                ("unknown-burn", "missionList/0/events/2/burn"),
                ("burn-not-on-edge", "missionList/0/events/1/burnStageSequence/0/burn"),
                (
                    "not-propulsive",
                    "missionList/0/events/2/burnStageSequence/1/element",
                ),
            ],
        )


class TestStructure(unittest.TestCase):
    def test_duplicate_identifiers(self):
        b = ScenarioBuilder()
        first, second = b.element("First"), b.element("Second")
        second.id = first.id
        b.lsp2.id = b.lsp.id
        b.lsp_lsp2.destination = b.lsp.id
        issues = [i for i in lint_scenario(b.build()) if i.code == "duplicate-id"]
        self.assertEqual(
            [i.path for i in issues],
            ["network/nodes/3", "instantiatedElements/1"],
        )
        self.assertIn("same identifier as the element First", issues[1].message)

    def test_an_element_may_share_the_identifier_of_its_template(self):
        b = ScenarioBuilder()
        element = b.element("Element")
        element.id = b.templates[0].id
        self.assertEqual(codes(b), [])

    def test_initial_containment(self):
        b = ScenarioBuilder()
        box = b.element("Box")
        outer = b.carrier("Outer")
        inner = b.carrier("Inner")
        b.instances[1].contents = [
            s.InstElementUUID(id=inner.id),
            s.InstElementUUID(id=box.id),
        ]
        b.instances[2].contents = [s.InstElementUUID(id=outer.id)]
        b.lsp.contents = [s.InstElementUUID(id=box.id)]
        self.assertEqual(
            codes(b),
            [
                ("multiple-containers", "network/nodes/2/contents/0"),
                ("containment-cycle", "instantiatedElements/1/contents"),
            ],
        )

    def test_warnings(self):
        b = ScenarioBuilder()
        stage = b.vehicle("Stage")
        element = b.element("Element")
        b.instances[-1].type = "Resource Container"
        b.lsp_lsp2.destination = b.lsp.id
        b.mission(
            [
                b.create([stage], b.leo),
                b.create([stage], b.leo, days=1),
                s.SpaceTransport(
                    name="Launch",
                    priority=2,
                    mission_time=timedelta(days=1),
                    location=b.leo.id,
                    edge=b.ksc_leo.id,
                    elements=[stage.id],
                    burn_stage_sequence=[],
                ),
            ]
        )
        self.assertEqual(codes(b, Severity.ERROR), [])
        self.assertEqual(
            codes(b, Severity.WARNING),
            [
                ("loop-edge", "network/edges/3"),
                ("template-type-mismatch", "instantiatedElements/1/type"),
                ("transport-location", "missionList/0/events/2/location"),
                ("created-twice", "missionList/0/events/1"),
            ],
        )
        self.assertIsNotNone(element)

    def test_paths_select_the_fields(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp, days=-1)], days=1)
        scenario = b.build()
        (issue,) = lint_scenario(scenario)
        data = scenario.model_dump(mode="json", by_alias=True)
        self.assertEqual(get_value(data, issue.path), "-P1D")


class TestSimulation(unittest.TestCase):
    def test_warnings_are_logged_by_their_events(self):
        b = ScenarioBuilder()
        stage = b.vehicle("Stage")
        b.mission(
            [
                b.create([stage], b.leo),
                b.create([stage], b.leo, days=2),
            ],
            name="Mission",
            days=5,
        )
        scenario = b.build()
        sim = FullSimulator(scenario)
        sim.simulate()
        warning = next(w for w in sim.warnings if "created by 2 events" in w.message)
        self.assertEqual(warning.time, 7)
        self.assertEqual(warning.event.source, (0, 1))
        analysis = MissionsAnalysis.create(scenario)
        self.assertIn(
            "Element Stage is created by 2 events.",
            analysis.missions[0].events[1].warnings,
        )

    def test_errors_prevent_simulation(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp, days=-1)], days=1)
        with self.assertRaisesRegex(ScenarioError, "before the start of its mission"):
            FullSimulator(b.build()).simulate()


class TestCommandLine(unittest.TestCase):
    def run_main(self, *paths):
        output = io.StringIO()
        with redirect_stdout(output):
            status = main([str(p) for p in paths])
        return status, output.getvalue()

    def test_clean_scenario(self):
        status, output = self.run_main(ROOT / REFERENCE_SCENARIOS[0])
        self.assertEqual(status, 0)
        self.assertIn("0 error(s), 0 warning(s)", output)

    def test_scenario_with_errors(self):
        b = ScenarioBuilder()
        b.mission([b.create([b.element()], b.lsp, days=-1)], days=1)
        path = ROOT / "build" / "lint_test_scenario.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(b.build().model_dump_json(by_alias=True), encoding="utf-8")
        try:
            status, output = self.run_main(path)
        finally:
            path.unlink()
        self.assertEqual(status, 1)
        self.assertIn(
            "Error [negative-time] missionList/0/events/0/missionTime: "
            "Event Create is before the start of its mission.",
            output,
        )
        self.assertIn("1 error(s), 0 warning(s)", output)

    def test_unreadable_scenario(self):
        status, output = self.run_main(ROOT / "README.md")
        self.assertEqual(status, 1)
        self.assertIn("README.md", output)


class TestErrorsHelper(unittest.TestCase):
    def test_errors_selects_errors(self):
        b = ScenarioBuilder()
        b.lsp_lsp2.destination = b.lsp.id
        b.mission([b.create([b.element()], b.lsp, days=-1)], days=1)
        issues = lint_scenario(b.build())
        self.assertEqual([i.code for i in errors(issues)], ["negative-time"])
        # errors are listed before warnings
        self.assertEqual(issues[0].severity, Severity.ERROR)
        self.assertEqual(START.year, 2030)


if __name__ == "__main__":
    unittest.main()
