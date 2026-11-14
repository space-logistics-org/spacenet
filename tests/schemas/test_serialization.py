"""
Tests that object schemas retain their content when serialized.
"""

import unittest
from datetime import timedelta
from uuid import uuid4

from spacenet import schemas as s


class TestStateDemandModels(unittest.TestCase):
    def test_state_demand_models_retain_type(self):
        state = s.State(
            name="Active",
            type="Active",
            demand_models=[
                s.InstRatedDemandModel(
                    name="Rated",
                    template_id=uuid4(),
                    demands=[
                        s.GenericResourceAmountRate(
                            class_of_supply=201, environment="Unpressurized", rate=2.0
                        )
                    ],
                ),
                s.InstSparingByMassDemandModel(
                    name="Sparing", template_id=uuid4(), pressurized_spares_rate=0.1
                ),
                s.InstTimedImpulseDemandModel(name="Impulse", template_id=uuid4()),
            ],
        )
        copy = s.State.model_validate_json(state.model_dump_json(by_alias=True))
        self.assertEqual(copy, state)
        self.assertIsInstance(copy.demand_models[0], s.InstRatedDemandModel)
        self.assertEqual(copy.demand_models[0].demands[0].rate, 2.0)
        self.assertIsInstance(copy.demand_models[1], s.InstSparingByMassDemandModel)
        self.assertEqual(copy.demand_models[1].pressurized_spares_rate, 0.1)
        self.assertIsInstance(copy.demand_models[2], s.InstTimedImpulseDemandModel)


class TestInstantiatedElement(unittest.TestCase):
    def test_parts_override_template(self):
        part = s.Part(
            resource=uuid4(), mean_time_to_repair=timedelta(hours=2), quantity=3
        )
        element = s.InstElement(name="Element", template_id=uuid4(), parts=[part])
        copy = s.InstElement.model_validate_json(element.model_dump_json(by_alias=True))
        self.assertEqual(copy.parts, [part])
        self.assertIsNone(s.InstElement(name="Element", template_id=uuid4()).parts)


class TestEvents(unittest.TestCase):
    def setUp(self):
        self.event = {
            "name": "Event",
            "priority": 1,
            "mission_time": timedelta(days=1),
            "location": uuid4(),
        }

    def test_surface_transport_state_is_optional(self):
        transport = s.SurfaceTransport(
            edge=uuid4(), vehicle=uuid4(), speed=1.5, **self.event
        )
        self.assertIsNone(transport.transport_state)
        self.assertEqual(transport.duty_cycle, 1)
        transport = s.SurfaceTransport(
            edge=uuid4(), vehicle=uuid4(), speed=1.5, transport_state=2, **self.event
        )
        self.assertEqual(transport.transport_state, 2)

    def test_exploration_additional_demands_are_resource_amounts(self):
        resource = uuid4()
        exploration = s.CrewedExploration(
            vehicle=uuid4(),
            eva_duration=timedelta(hours=8),
            duration=timedelta(days=7),
            eva_per_week=5,
            element_states=[],
            additional_demands=[
                s.ResourceAmount(resource=resource, amount=2),
                s.GenericResourceAmount(
                    class_of_supply=203, environment="Unpressurized", amount=1
                ),
            ],
            **self.event,
        )
        copy = s.CrewedExploration.model_validate_json(
            exploration.model_dump_json(by_alias=True)
        )
        self.assertEqual(copy.additional_demands[0].resource, resource)
        self.assertEqual(copy.additional_demands[1].class_of_supply, 203)
        self.assertEqual(
            s.CrewedExploration(
                vehicle=uuid4(),
                eva_duration=timedelta(hours=8),
                duration=timedelta(days=7),
                eva_per_week=5,
                element_states=[],
                **self.event,
            ).additional_demands,
            [],
        )


class TestScenario(unittest.TestCase):
    def test_description_is_optional(self):
        scenario = s.Scenario(
            name="Scenario",
            created_by="Test",
            start_date="2030-01-01T00:00:00Z",
            scenario_type="Lunar",
        )
        self.assertIsNone(scenario.description)
        copy = s.Scenario.model_validate_json(scenario.model_dump_json(by_alias=True))
        self.assertEqual(copy, scenario)


if __name__ == "__main__":
    unittest.main()
