"""
Tests of the validation of engineering models against published data.
"""

import math
import sys
import unittest

from spacenet import schemas as s
from spacenet.simulation.events import get_required_fuel_mass
from spacenet.validation import (
    CheckKind,
    CheckStatus,
    Reference,
    compare,
    failures,
    max_payload,
    number,
    report_markdown,
)

from ..simulation.util import ROOT, ScenarioBuilder

sys.path.insert(0, str(ROOT / "artemis"))

# pylint: disable=wrong-import-position,import-error
import validation as artemis_validation  # noqa: E402


class TestCompare(unittest.TestCase):
    def test_value_with_tolerance(self):
        reference = Reference("x", "Quantity", 100.0, "kg", "Source")
        result = compare(reference, 104.0, tolerance=0.05)
        self.assertEqual(result.status, CheckStatus.PASS)
        self.assertAlmostEqual(result.difference, 0.04)
        result = compare(reference, 94.0, tolerance=0.05)
        self.assertEqual(result.status, CheckStatus.FAIL)
        self.assertAlmostEqual(result.difference, -0.06)

    def test_ranges_and_bounds(self):
        reference = Reference("x", "Quantity", (8.0, 14.0), "flights", "Source")
        self.assertEqual(compare(reference, 9).difference, 0)
        self.assertEqual(compare(reference, 16).status, CheckStatus.FAIL)
        minimum = Reference("y", "Quantity", (27_000.0, None), "kg", "Source")
        self.assertEqual(compare(minimum, 30_000).status, CheckStatus.PASS)
        self.assertEqual(minimum.describe(), ">= 27,000")
        maximum = Reference("z", "Quantity", (None, 6_000.0), "kg", "Source")
        self.assertEqual(compare(maximum, 6_500).status, CheckStatus.FAIL)
        self.assertEqual(maximum.describe(), "<= 6,000")

    def test_report(self):
        reference = Reference("x", "Mass", 0.89, "kg", "Paper", "https://x")
        text = report_markdown([compare(reference, 0.89, CheckKind.INPUT)])
        self.assertIn(
            "| Mass (kg) | 0.8900 | 0.8900 | +0.0% | input | pass | [Paper](https://x) |",
            text,
        )
        self.assertEqual(number(25_566.4), "25,566")
        self.assertEqual(number(3.857), "3.857")


class TestMaxPayload(unittest.TestCase):
    def test_matches_the_rocket_equation(self):
        def build(payload):
            b = ScenarioBuilder()
            stage = b.vehicle(mass=1000, fuel=9000, isp=300)
            cargo = b.element("Payload", mass=payload)
            b.mission(
                [
                    b.create([stage, cargo], b.leo),
                    s.PropulsiveBurn(
                        name="Burn",
                        priority=2,
                        mission_time=0,
                        location=b.leo.id,
                        elements=[stage.id, cargo.id],
                        burn=b.burn.id,
                        burn_stage_sequence=[
                            s.BurnStageItem(type="Burn", element=stage.id)
                        ],
                    ),
                ]
            )
            return b.build()

        payload = max_payload(build, 100_000, precision=1)
        # 9000 kg of fuel achieves 1000 m/s for a total mass of 9000 / (1 - exp(-1000 / (300 g0)))
        self.assertAlmostEqual(
            get_required_fuel_mass(10_000 + payload, 1000, 300), 9000, delta=5
        )
        self.assertTrue(math.isnan(max_payload(lambda m: build(1e9), 1e10)))


class TestArtemisValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = artemis_validation.validate()
        cls.by_key = {r.reference.key: r for r in cls.results}

    def test_campaign_matches_published_data(self):
        self.assertEqual(
            [(r.reference.key, r.model, r.difference) for r in failures(self.results)],
            [],
        )

    def test_independent_checks(self):
        block_1 = self.by_key["sls_block_1_tli"]
        self.assertEqual(block_1.kind, CheckKind.VALIDATED)
        # the simulated Block 1 capability is about 5% below the published 27 t
        self.assertAlmostEqual(block_1.difference, -0.053, delta=0.01)
        self.assertEqual(self.by_key["hls_tankers"].model, 9)
        self.assertGreater(self.by_key["orion_capability"].model, 1_000)

    def test_every_reference_is_checked(self):
        self.assertEqual(set(self.by_key), set(artemis_validation.REFERENCES))
        for reference in artemis_validation.REFERENCES.values():
            self.assertTrue(reference.source and reference.url, reference.key)

    def test_default_consumables_overstate_oxygen(self):
        results = {
            r.reference.key: r for r in artemis_validation.compare_default_consumables()
        }
        self.assertEqual(results["water_rate"].status, CheckStatus.PASS)
        self.assertEqual(results["food_rate"].status, CheckStatus.PASS)
        # the reference implementation's oxygen rate is about 4x metabolic needs
        self.assertEqual(results["oxygen_rate"].status, CheckStatus.FAIL)
        self.assertGreater(results["oxygen_rate"].difference, 3)
