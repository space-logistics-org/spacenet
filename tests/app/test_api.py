"""
Tests of the application programming interface of the web application.
"""

import json
import unittest
from datetime import datetime, timedelta

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

# pylint: disable=wrong-import-position
from fastapi import FastAPI
from fastapi.testclient import TestClient

from spacenet.simulation import FullSimulator
from spacenet_app.api import add_exception_handlers, router

from ..simulation.util import ROOT, load_scenario

SCENARIOS = (
    "quick_start/completed_quick_start_1_w_db.json",
    "quick_start/completed_quick_start_1_wo_db.json",
    "quick_start/completed_quick_start_2_w_db.json",
    "quick_start/completed_quick_start_3_wo_db.json",
    "artemis/artemis_campaign.json",
    "artemis/artemis_add_campaign.json",
)
QUICK_START_2 = SCENARIOS[2]
ADD_CAMPAIGN = "artemis/artemis_add_campaign.json"


def load_json(path: str) -> dict:
    """Loads a scenario file as it would be sent by a browser."""
    with open(ROOT / path, encoding="utf-8") as scenario_file:
        return json.load(scenario_file)


class ApiTestCase(unittest.TestCase):
    """Base class for tests of the interface without the user database."""

    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router, prefix="/api")
        add_exception_handlers(app)
        cls.client = TestClient(app)

    def post(self, path: str, status: int = 200, **body):
        """Posts a request and returns the decoded response."""
        response = self.client.post(f"/api{path}", json=body)
        self.assertEqual(response.status_code, status, response.text[:500])
        return response.json()


class TestMeta(ApiTestCase):
    def test_schema(self):
        schema = self.client.get("/api/meta/schema").json()
        self.assertIn("missionList", schema["properties"])
        self.assertIn("Configuration", schema["$defs"])
        self.assertIn("Manifest", schema["$defs"])

    def test_enumerations(self):
        enums = self.client.get("/api/meta/enums").json()
        self.assertEqual(len(enums["eventTypes"]), 14)
        self.assertEqual(len(enums["containerTypes"]), 9)
        self.assertIn("OMS Oxidizer", enums["tankSelectors"])
        self.assertIn("Fill Destination", enums["transferModes"])
        self.assertIn(
            {"id": 201, "name": "Water and Support Equipment", "base": 2},
            enums["classesOfSupply"],
        )
        lunar = next(t for t in enums["scenarioTypes"] if t["name"] == "Lunar")
        self.assertEqual(lunar["bodies"], ["Earth", "Moon"])

    def test_defaults(self):
        scenario = self.client.get("/api/meta/defaults").json()
        self.assertEqual(scenario["missionList"], [])
        self.assertEqual(scenario["configuration"]["timePrecision"], 0.05)
        self.assertEqual(scenario["manifest"], {"containers": [], "loads": []})
        self.post("/scenario/validate", scenario=scenario)


class TestScenario(ApiTestCase):
    def test_validate_example_scenarios(self):
        for path in SCENARIOS:
            scenario = load_json(path)
            validated = self.post("/scenario/validate", scenario=scenario)
            self.assertEqual(validated["name"], scenario["name"])
            self.assertEqual(
                len(validated["missionList"]), len(scenario["missionList"])
            )
            # a validated scenario is a fixed point
            self.assertEqual(
                self.post("/scenario/validate", scenario=validated), validated
            )

    def test_invalid_schema(self):
        scenario = load_json(SCENARIOS[0])
        scenario["missionList"][0]["events"][3]["priority"] = 9
        detail = self.post("/scenario/validate", 422, scenario=scenario)["detail"]
        self.assertEqual(
            detail[0]["loc"][:5], ["body", "scenario", "missionList", 0, "events"]
        )
        self.assertEqual(detail[0]["loc"][-1], "priority")

    def test_unknown_reference(self):
        scenario = load_json(SCENARIOS[0])
        event = scenario["missionList"][0]["events"][2]
        event["location"] = "00000000-0000-0000-0000-000000000000"
        for path in (
            "/scenario/validate",
            "/missions/analyze",
            "/simulate",
            "/demands/analyze",
            "/manifest/view",
        ):
            detail = self.post(path, 422, scenario=scenario)["detail"]
            self.assertEqual(detail[0]["type"], "scenario_error")
            self.assertEqual(detail[0]["missionIndex"], 0)
            self.assertEqual(detail[0]["eventIndex"], 2)
            self.assertIn("unknown location", detail[0]["msg"])

    def test_load_database(self):
        for name in ("quick_start_1.xlsx", "quick_start_2.xlsx"):
            with open(ROOT / "quick_start" / name, "rb") as database:
                response = self.client.post(
                    "/api/library/database", files={"upload": (name, database)}
                )
            self.assertEqual(response.status_code, 200, response.text[:500])
            library = response.json()
            self.assertGreater(len(library["nodes"]), 0)
            self.assertGreater(len(library["edges"]), 0)
            self.assertGreater(len(library["elements"]), 0)
            self.assertIn("classOfSupply", library["resources"][0])
            if name != "quick_start_1.xlsx":
                continue
            # propulsion systems with separate, shared, and single fuel tanks
            vehicles = {e["name"]: e for e in library["elements"]}
            oms, rcs = vehicles["Altair DM"]["propulsionSystems"]
            self.assertEqual((oms["type"], oms["isp"]), ("OMS", 448))
            self.assertEqual(oms["fuelTank"]["maxAmount"], 24900)
            self.assertEqual((rcs["type"], rcs["isp"]), ("RCS", 300))
            self.assertEqual(rcs["fuelTank"]["contents"]["amount"], 425)
            oms, rcs = vehicles["Orion SM"]["propulsionSystems"]
            self.assertEqual(rcs["sharedFuelTank"], "OMS")
            self.assertIsNone(rcs["fuelTank"])
            (rcs,) = vehicles["Orion CM"]["propulsionSystems"]
            self.assertEqual((rcs["type"], rcs["isp"]), ("RCS", 301))
            burns = [b["type"] for e in library["edges"] for b in e.get("burns", [])]
            self.assertEqual(burns.count("RCS"), 7)
            self.assertEqual(burns.count("OMS"), 8)

    def test_invalid_database(self):
        response = self.client.post(
            "/api/library/database", files={"upload": ("x.xlsx", b"not a spreadsheet")}
        )
        self.assertEqual(response.status_code, 422)

    def test_validate_models(self):
        # the object models of a scenario are valid and returned as they are
        scenario = self.post("/scenario/validate", scenario=load_json(QUICK_START_2))
        models = {
            "nodes": scenario["network"]["nodes"],
            "edges": scenario["network"]["edges"],
            "resources": scenario["resourceList"],
            "elements": scenario["elementTemplates"],
            "demandModels": scenario["demandModels"],
        }
        for kind, items in models.items():
            self.assertGreater(len(items), 0, kind)
            for item in items:
                self.assertEqual(
                    self.post(f"/library/{kind}/validate", model=item), item
                )

    def test_validate_new_model(self):
        node = self.post(
            "/library/nodes/validate",
            model={
                "type": "Surface Node",
                "name": "Base",
                "latitude": -89.5,
                "longitude": 0,
            },
        )
        self.assertEqual(node["body1"], "Earth")
        self.assertEqual(len(node["id"]), 36)
        model = self.post(
            "/library/demandModels/validate",
            model={"type": "Crew Consumables", "name": "Crew"},
        )
        self.assertEqual(model["waterRecoveryRate"], 0.42)

    def test_validate_invalid_model(self):
        detail = self.post(
            "/library/nodes/validate",
            422,
            model={"type": "Surface Node", "name": "Base", "latitude": 91},
        )["detail"]
        self.assertEqual(
            sorted(item["loc"][0] for item in detail), ["latitude", "longitude"]
        )
        # the type must be one of the kind of model
        detail = self.post(
            "/library/edges/validate", 422, model={"type": "Surface Node", "name": "x"}
        )["detail"]
        self.assertIn("Unknown type", detail[0]["msg"])
        self.post("/library/planets/validate", 422, model={"name": "x"})


class TestAnalysis(ApiTestCase):
    def test_missions(self):
        for path in SCENARIOS:
            scenario = load_json(path)
            analysis = self.post("/missions/analyze", scenario=scenario)
            self.assertEqual(len(analysis["missions"]), len(scenario["missionList"]))
            self.assertEqual(
                [i for i in analysis["issues"] if i["kind"] != "warning"], []
            )
            for mission, summary in zip(scenario["missionList"], analysis["missions"]):
                self.assertEqual(len(summary["events"]), len(mission["events"]))

    def test_mission_errors_reference_events(self):
        scenario = load_json(SCENARIOS[0])
        events = scenario["missionList"][0]["events"]
        index = next(i for i, e in enumerate(events) if e["type"] == "Create Elements")
        del events[index]
        analysis = self.post("/missions/analyze", scenario=scenario)
        errors = [i for i in analysis["issues"] if i["kind"] == "spatial"]
        self.assertGreater(len(errors), 0)
        for error in errors:
            self.assertEqual(error["missionIndex"], 0)
            self.assertIsNotNone(error["eventIndex"])
            summary = analysis["missions"][0]["events"][error["eventIndex"]]
            self.assertIn(error["message"], summary["errors"])
        self.assertEqual(analysis["missions"][0]["errorCount"], len(errors))

    def test_state_before_event(self):
        scenario = load_json(SCENARIOS[0])
        events = scenario["missionList"][0]["events"]
        index = next(i for i, e in enumerate(events) if e["type"] == "Space Transport")
        event = events[index]
        state = self.post(
            "/events/state",
            scenario=scenario,
            missionIndex=0,
            missionTime=event["missionTime"],
            priority=event["priority"],
            excludeEventIndex=index,
        )
        origin = next(l for l in state["locations"] if l["id"] == event["location"])
        present = set()

        def visit(element):
            present.add(element["id"])
            for child in element["contents"]:
                visit(child)

        for element in origin["elements"]:
            visit(element)
        self.assertTrue(set(event["elements"]) <= present)
        self.post(
            "/events/state", 422, scenario=scenario, missionIndex=7, missionTime="PT0S"
        )

    def test_evaluate_space_transport(self):
        scenario = load_json("artemis/artemis_campaign.json")
        mission_index = 2
        events = scenario["missionList"][mission_index]["events"]
        index = next(i for i, e in enumerate(events) if e["type"] == "Space Transport")
        event = events[index]
        evaluation = self.post(
            "/events/evaluate",
            scenario=scenario,
            missionIndex=mission_index,
            eventIndex=index,
            event=event,
        )
        self.assertEqual(evaluation["issues"], [])
        self.assertGreater(len(evaluation["burns"]), 0)
        for burn in evaluation["burns"]:
            self.assertTrue(burn["executed"])
            self.assertAlmostEqual(burn["deltaVRemaining"], 0, 5)
            self.assertAlmostEqual(burn["deltaVAchieved"], burn["deltaVRequired"], 5)
        self.assertGreater(evaluation["transport"]["duration"], 0)
        self.assertEqual(
            evaluation["next"]["location"], evaluation["transport"]["destination"]
        )

        # without a burn sequence no delta-v is achieved
        draft = dict(event, burnStageSequence=[])
        evaluation = self.post(
            "/events/evaluate",
            scenario=scenario,
            missionIndex=mission_index,
            eventIndex=index,
            event=draft,
        )
        first = evaluation["burns"][0]
        self.assertEqual(first["deltaVRemaining"], first["deltaVRequired"])
        self.assertIn("Insufficient delta-v", evaluation["issues"][0]["message"])

    def test_evaluate_invalid_event(self):
        scenario = load_json(SCENARIOS[0])
        event = dict(scenario["missionList"][0]["events"][0], type="Unknown")
        detail = self.post(
            "/events/evaluate", 422, scenario=scenario, missionIndex=0, event=event
        )["detail"]
        self.assertEqual(detail[0]["loc"][:2], ["body", "event"])

    def test_demands(self):
        scenario = load_json(QUICK_START_2)
        analysis = self.post("/demands/analyze", scenario=scenario)
        self.assertEqual(len(analysis["raw"]["demands"]), 44)
        self.assertEqual(
            sum(len(n["consumption"]) for n in analysis["aggregated"]["nodes"]), 30
        )
        self.assertEqual(len(analysis["supplyEdges"]), 6)
        self.assertEqual(len(analysis["byMission"]), 2)
        packed = self.post(
            "/demands/analyze",
            scenario=scenario,
            options={"estimateContainerMasses": True},
        )
        self.assertGreater(packed["totalMass"], analysis["totalMass"])

    def test_simulate(self):
        for path in SCENARIOS:
            scenario = load_scenario(path)
            simulator = FullSimulator(scenario)
            simulator.simulate()
            response = self.client.post(
                "/api/simulate", json={"scenario": load_json(path)}
            )
            self.assertEqual(response.status_code, 200)
            self.assertLess(len(response.content), 600_000)
            analysis = response.json()
            self.assertEqual(analysis["errorCount"], 0)
            totals = analysis["totals"]
            self.assertAlmostEqual(totals["launchMass"], simulator.total_launch_mass)
            self.assertAlmostEqual(totals["crewTime"], simulator.total_crew_time)
            self.assertAlmostEqual(
                totals["relativeExplorationCapability"],
                simulator.total_relative_exploration_capability,
            )
            self.assertEqual(
                len(analysis["history"]["frames"]), len(simulator.network_history)
            )
            propellant = analysis["propellant"]
            self.assertEqual(len(propellant["tanks"]), len(propellant["budgets"]))
            self.assertIn("propellantBurnedMass", totals)
            self.assertEqual(
                len(analysis["isru"]["processes"]),
                len({(r.element_id, r.process) for r in simulator.isru_records}),
            )
            self.assertAlmostEqual(
                totals["isruOutputMass"],
                sum(r.output_mass for r in simulator.isru_records),
            )


class TestReliability(ApiTestCase):
    def test_run_monte_carlo(self):
        scenario = load_json(ADD_CAMPAIGN)
        result = self.post(
            "/reliability/run", scenario=scenario, study={"runs": 6, "seed": 2}
        )
        self.assertEqual(result["runs"], 6)
        self.assertEqual(result["failedRuns"], 0)
        parts = {part["part"]: part for part in result["parts"]}
        self.assertEqual(set(parts), {"Electrolyzer Stack", "Excavator Drive Actuator"})
        self.assertAlmostEqual(parts["Electrolyzer Stack"]["expected"], 0.6108, 3)
        self.assertEqual(sum(parts["Electrolyzer Stack"]["histogram"]), 6)

    def test_invalid_study(self):
        self.post(
            "/reliability/run",
            status=422,
            scenario=load_json(ADD_CAMPAIGN),
            study={"runs": 0},
        )


class TestTrades(ApiTestCase):
    def test_metrics(self):
        metrics = self.client.get("/api/trades/metrics").json()
        self.assertIn("campaignCost", metrics)
        self.assertIn("errorCount", metrics)

    def test_run_trade(self):
        scenario = load_json(ADD_CAMPAIGN)
        result = self.post(
            "/trades/run",
            scenario=scenario,
            study={
                "variables": [
                    {
                        "name": "descent",
                        "path": "network/edges/name=LLO-LSP/burns/1/deltaV",
                        "values": [2030, 2300],
                    }
                ],
                "metrics": ["errorCount", "propellantBurnedMass"],
            },
        )
        errors = [case["metrics"]["errorCount"] for case in result["cases"]]
        # the landers cannot achieve a descent of 2,300 m/s
        self.assertEqual(errors[0], 0)
        self.assertGreater(errors[1], 0)

    def test_invalid_path(self):
        self.post(
            "/trades/run",
            status=422,
            scenario=load_json(ADD_CAMPAIGN),
            study={"variables": [{"name": "x", "path": "nothing/here", "values": [1]}]},
        )


class TestPropellant(ApiTestCase):
    def test_size_tankers(self):
        sizing = self.post(
            "/propellant/tankers",
            required=100_000,
            tankerDelivery=15_000,
            depotCapacity=120_000,
            boiloffRate=0.001,
            intervalDays=10,
            loiterDays=5,
        )
        self.assertTrue(sizing["feasible"])
        self.assertEqual(sizing["flights"], 8)
        self.assertGreaterEqual(sizing["final"], 100_000)
        self.assertEqual(sizing["timeline"][0], [0, 0])

    def test_invalid_tanker_request(self):
        self.post("/propellant/tankers", status=422, required=100, tankerDelivery=0)
        self.post(
            "/propellant/tankers",
            status=422,
            required=100,
            tankerDelivery=10,
            transferLoss=1,
        )

    def test_evaluate_fill_transfer(self):
        scenario = load_json(ADD_CAMPAIGN)
        missions = scenario["missionList"]
        mission_index, event_index = next(
            (m, e)
            for m, mission in enumerate(missions)
            for e, event in enumerate(mission["events"])
            if event.get("transferMode") == "Fill Destination"
        )
        evaluation = self.post(
            "/events/evaluate",
            scenario=scenario,
            missionIndex=mission_index,
            eventIndex=event_index,
            event=missions[mission_index]["events"][event_index],
        )
        self.assertEqual(evaluation["issues"], [])
        self.assertGreater(len(evaluation["transfers"]), 0)
        self.assertTrue(all(t["delivered"] > 0 for t in evaluation["transfers"]))


class TestManifest(ApiTestCase):
    def test_operations(self):
        scenario = load_json(QUICK_START_2)

        def post(path, **body):
            result = self.post(f"/manifest{path}", scenario=scenario, **body)
            # the client stores the manifest in the scenario
            scenario["manifest"] = result["manifest"]
            return result

        result = post("/view")
        self.assertEqual(len(result["view"]["demands"]), 30)
        self.assertEqual(result["manifest"], {"containers": [], "loads": []})
        demand = next(d for d in result["view"]["demands"] if d["classOfSupply"] == 202)

        result = post("/containers", containerType="Cargo Transfer Bag", count=2)
        first, second = [c["id"] for c in result["view"]["containers"]]
        self.assertEqual(
            [c["name"] for c in result["view"]["containers"]], ["CTB 1", "CTB 2"]
        )

        result = post("/view", selection={"containerId": first})
        packable = [d["key"] for d in result["view"]["demands"] if d["canPack"]]
        self.assertIn(demand["key"], packable)

        result = post("/pack", demandKeys=[demand["key"]], containerId=first)
        packed = next(d for d in result["view"]["demands"] if d["key"] == demand["key"])
        self.assertAlmostEqual(packed["packedAmount"], 26.8)
        self.assertTrue(packed["canUnpack"])
        container = result["view"]["containers"][0]
        self.assertAlmostEqual(container["cargoMass"], 26.8)
        self.assertEqual(container["pointKey"], demand["pointKey"])

        # load the container on a transport which arrives at its supply point
        loaded = None
        for edge in result["view"]["edges"]:
            for carrier in edge["carriers"]:
                selection = {"edgeKey": edge["key"], "carrierId": carrier["id"]}
                view = post("/view", selection=selection)["view"]
                if view["containers"][0]["canManifest"]:
                    loaded = selection
                    break
            if loaded:
                break
        self.assertIsNotNone(loaded)
        result = post("/load", containerIds=[first], **loaded)
        self.assertEqual(
            result["view"]["containers"][0]["edgeKeys"], [loaded["edgeKey"]]
        )
        self.assertEqual(len(result["manifest"]["loads"]), 1)
        self.assertEqual(result["view"]["loadedContainerCount"], 1)

        result = post("/unload", containerIds=[first], edgeKey=loaded["edgeKey"])
        self.assertEqual(result["manifest"]["loads"], [])
        result = post("/unpack", demandKeys=[demand["key"]])
        self.assertEqual(result["view"]["containers"][0]["contents"], [])
        result = post("/containers/remove", containerIds=[second])
        self.assertEqual(len(result["view"]["containers"]), 1)

        result = post("/auto-pack", demandKeys=[demand["key"]])
        packed = next(d for d in result["view"]["demands"] if d["key"] == demand["key"])
        self.assertEqual(packed["remainingAmount"], 0)

        result = post("/auto")
        self.assertTrue(
            all(d["remainingAmount"] == 0 for d in result["view"]["demands"])
        )
        self.assertGreater(result["view"]["loadedContainerCount"], 0)
        self.assertEqual(result["dropped"], [])
        # the manifest reduces the unsatisfied demands of the simulation
        baseline = self.post("/simulate", scenario=load_json(QUICK_START_2))
        analysis = self.post("/simulate", scenario=scenario)
        self.assertEqual(analysis["errorCount"], 0)

        def mass(result):
            return sum(1 for i in result["issues"] if i["kind"] == "demand")

        self.assertLessEqual(mass(analysis), mass(baseline))

        result = post("/reset")
        self.assertEqual(result["manifest"], {"containers": [], "loads": []})

    def test_unknown_keys(self):
        scenario = load_json(QUICK_START_2)
        detail = self.post(
            "/manifest/auto-pack", 422, scenario=scenario, demandKeys=["x"]
        )["detail"]
        self.assertEqual(detail[0]["type"], "value_error")
        self.post(
            "/manifest/load",
            422,
            scenario=scenario,
            containerIds=[],
            edgeKey="x",
            carrierId="00000000-0000-0000-0000-000000000000",
        )

    def test_stale_manifest(self):
        scenario = load_json(QUICK_START_2)
        scenario["manifest"] = self.post("/manifest/auto", scenario=scenario)[
            "manifest"
        ]
        for mission in scenario["missionList"]:
            start = datetime.fromisoformat(mission["startDate"].replace("Z", "+00:00"))
            mission["startDate"] = (start + timedelta(days=1)).isoformat()
        result = self.post("/manifest/view", scenario=scenario)
        self.assertGreater(len(result["dropped"]), 0)
        self.assertEqual(result["manifest"]["loads"], [])


class TestExports(ApiTestCase):
    def _export(self, path, **body):
        response = self.client.post(f"/api/export{path}", json=body)
        self.assertEqual(response.status_code, 200, response.text[:500])
        self.assertIn("attachment", response.headers["content-disposition"])
        return response.text.splitlines()

    def test_demands(self):
        scenario = load_json(QUICK_START_2)
        lines = self._export("/demands/raw", scenario=scenario)
        self.assertEqual(
            lines[0], "Time,Location,Element,Resource,Amount,Units,Mass (kg)"
        )
        self.assertEqual(len(lines), 92)
        lines = self._export("/demands/aggregated", scenario=scenario, delimiter=";")
        self.assertTrue(lines[0].startswith("Time 1;Time 2;Node 1;Node 2"))
        self.assertEqual(len(lines), 31)

    def test_manifest(self):
        scenario = load_json(QUICK_START_2)
        scenario["manifest"] = self.post("/manifest/auto", scenario=scenario)[
            "manifest"
        ]
        counts = {}
        for level in ("demands", "containers", "carriers", "edges"):
            lines = self._export("/manifest", scenario=scenario, level=level)
            self.assertTrue(lines[0].startswith("Origin,Departure,Destination,Arrival"))
            counts[level] = len(lines)
        self.assertEqual(counts["edges"], 7)
        self.assertGreater(counts["demands"], counts["containers"])
        self.assertGreater(counts["containers"], counts["carriers"])
        response = self.client.post(
            "/api/export/manifest", json={"scenario": scenario, "level": "x"}
        )
        self.assertEqual(response.status_code, 422)
        response = self.client.post(
            "/api/export/manifest", json={"scenario": scenario, "delimiter": "|"}
        )
        self.assertEqual(response.status_code, 422)

    def test_propellant(self):
        lines = self._export("/propellant", scenario=load_json(ADD_CAMPAIGN))
        self.assertTrue(lines[0].startswith("Vehicle,Tank,Resource"))
        self.assertGreater(len(lines), 10)
