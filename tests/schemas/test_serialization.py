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


class TestVehicles(unittest.TestCase):
    def setUp(self):
        self.fuel = {"classOfSupply": 101, "environment": "Unpressurized"}
        self.tank = {"maxAmount": 100, "contents": dict(self.fuel, amount=80)}
        self.vehicle = {
            "name": "Stage",
            "type": "Propulsive Vehicle",
            "mass": 1000,
            "volume": 0,
            "maxCargoMass": 0,
            "maxCargoVolume": 0,
            "maxCrew": 0,
        }

    def _vehicle(self, systems):
        return s.PropulsiveVehicle.model_validate(
            dict(self.vehicle, propulsionSystems=systems)
        )

    def test_propulsion_systems(self):
        vehicle = self._vehicle(
            [
                {"type": "OMS", "isp": 320, "fuelTank": self.tank},
                {"type": "RCS", "isp": 300, "sharedFuelTank": "OMS"},
            ]
        )
        oms, rcs = vehicle.propulsion_systems
        self.assertEqual(oms.type, s.PropulsionType.OMS)
        self.assertEqual(oms.fuel_tank.max_amount, 100)
        self.assertEqual(oms.fuel_tank.contents.amount, 80)
        self.assertIsNone(rcs.fuel_tank)
        self.assertEqual(rcs.shared_fuel_tank, s.PropulsionType.OMS)
        data = vehicle.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertEqual(
            data["propulsionSystems"][1],
            {"type": "RCS", "isp": 300.0, "sharedFuelTank": "OMS"},
        )
        self.assertNotIn("isp", data)
        self.assertEqual(s.PropulsiveVehicle.model_validate(data), vehicle)

    def test_bipropellant_systems(self):
        oxidizer = {"maxAmount": 300, "contents": dict(self.fuel, amount=240)}
        vehicle = self._vehicle(
            [
                {
                    "type": "OMS",
                    "isp": 350,
                    "mixtureRatio": 3,
                    "fuelTank": dict(self.tank, boiloffRate=0.001),
                    "oxidizerTank": oxidizer,
                },
                {
                    "type": "RCS",
                    "isp": 300,
                    "mixtureRatio": 1.6,
                    "sharedFuelTank": "OMS",
                    "sharedOxidizerTank": "OMS",
                },
            ]
        )
        oms, rcs = vehicle.propulsion_systems
        self.assertTrue(oms.is_bipropellant)
        self.assertEqual(oms.fuel_tank.boiloff_rate, 0.001)
        self.assertEqual(oms.oxidizer_tank.max_amount, 300)
        self.assertEqual(rcs.shared_oxidizer_tank, s.PropulsionType.OMS)
        data = vehicle.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertEqual(data["propulsionSystems"][0]["fuelTank"]["boiloffRate"], 0.001)
        self.assertEqual(s.PropulsiveVehicle.model_validate(data), vehicle)

    def test_invalid_bipropellant_systems(self):
        oxidizer = {"maxAmount": 300, "contents": dict(self.fuel, amount=240)}
        oms = {"type": "OMS", "isp": 320, "fuelTank": self.tank}
        for systems in (
            # oxidizer tank without mixture ratio and vice versa
            [dict(oms, oxidizerTank=oxidizer)],
            [dict(oms, mixtureRatio=3)],
            # both an oxidizer tank and a shared oxidizer tank
            [
                dict(
                    oms, mixtureRatio=3, oxidizerTank=oxidizer, sharedOxidizerTank="RCS"
                )
            ],
            # shared oxidizer tank which does not exist
            [
                oms,
                {
                    "type": "RCS",
                    "isp": 300,
                    "mixtureRatio": 2,
                    "sharedFuelTank": "OMS",
                    "sharedOxidizerTank": "OMS",
                },
            ],
            [dict(oms, mixtureRatio=3, sharedOxidizerTank="OMS")],
            # invalid boiloff rate
            [dict(oms, fuelTank=dict(self.tank, boiloffRate=2))],
        ):
            with self.subTest(systems=systems), self.assertRaises(ValueError):
                self._vehicle(systems)

    def test_monopropellant_dump_is_unchanged(self):
        vehicle = self._vehicle([{"type": "OMS", "isp": 320, "fuelTank": self.tank}])
        data = vehicle.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertEqual(
            data["propulsionSystems"],
            [
                {
                    "type": "OMS",
                    "isp": 320.0,
                    "fuelTank": {
                        "maxAmount": 100.0,
                        "contents": dict(self.fuel, amount=80.0),
                    },
                }
            ],
        )

    def test_transfer_resources_options(self):
        event = {
            "name": "Refuel",
            "type": "Transfer Resources",
            "priority": 1,
            "missionTime": 0,
            "location": str(uuid4()),
            "originContainer": str(uuid4()),
            "destinationContainer": str(uuid4()),
        }
        transfer = s.TransferResources.model_validate(
            dict(
                event,
                transferMode="Fill Destination",
                destinationTank="OMS Oxidizer",
                lossFraction=0.02,
            )
        )
        self.assertEqual(transfer.resources, [])
        self.assertEqual(transfer.transfer_mode, s.TransferMode.FILL_DESTINATION)
        self.assertEqual(transfer.destination_tank, s.TankSelector.OMS_OXIDIZER)
        self.assertTrue(transfer.destination_tank.is_oxidizer)
        self.assertEqual(
            transfer.destination_tank.propulsion_type, s.PropulsionType.OMS
        )
        with self.assertRaises(ValueError):
            s.TransferResources.model_validate(dict(event, lossFraction=1))
        data = s.TransferResources.model_validate(event).model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        for key in ("originTank", "destinationTank", "transferMode", "lossFraction"):
            self.assertNotIn(key, data)

    def test_invalid_propulsion_systems(self):
        oms = {"type": "OMS", "isp": 320, "fuelTank": self.tank}
        for systems in (
            [],
            # duplicate types
            [oms, oms],
            # neither or both of the fuel tank and the shared fuel tank
            [oms, {"type": "RCS", "isp": 300}],
            [
                oms,
                {
                    "type": "RCS",
                    "isp": 300,
                    "fuelTank": self.tank,
                    "sharedFuelTank": "OMS",
                },
            ],
            # shared fuel tank which does not exist
            [{"type": "RCS", "isp": 300, "sharedFuelTank": "OMS"}],
            [{"type": "RCS", "isp": 300, "sharedFuelTank": "RCS"}],
            [
                {"type": "OMS", "isp": 300, "sharedFuelTank": "RCS"},
                {"type": "RCS", "isp": 300, "sharedFuelTank": "OMS"},
            ],
        ):
            with self.subTest(systems=systems), self.assertRaises(ValueError):
                self._vehicle(systems)

    def test_surface_vehicle_fuel_tank(self):
        rover = s.SurfaceVehicle.model_validate(
            dict(self.vehicle, type="Surface Vehicle", maxSpeed=10, fuelTank=self.tank)
        )
        self.assertEqual(rover.fuel_tank.contents.class_of_supply, 101)
        data = rover.model_dump(mode="json", by_alias=True, exclude_none=True)
        self.assertEqual(data["fuelTank"]["maxAmount"], 100)
        self.assertNotIn("maxFuel", data)

    def test_legacy_vehicle_templates_are_upgraded(self):
        legacy = dict(
            self.vehicle, isp=320, maxFuel=100, fuel=dict(self.fuel, amount=80)
        )
        vehicle = s.PropulsiveVehicle.model_validate(legacy)
        (system,) = vehicle.propulsion_systems
        self.assertEqual((system.type, system.isp), (s.PropulsionType.OMS, 320))
        self.assertEqual(system.fuel_tank.max_amount, 100)
        self.assertEqual(system.fuel_tank.contents.amount, 80)
        rover = s.SurfaceVehicle.model_validate(
            dict(legacy, type="Surface Vehicle", maxSpeed=10)
        )
        self.assertEqual(rover.fuel_tank.max_amount, 100)
        self.assertEqual(rover.fuel_tank.contents.amount, 80)

    def test_legacy_instantiated_vehicles_are_upgraded(self):
        template_id, rover_id = str(uuid4()), str(uuid4())
        fuel = dict(self.fuel, amount=80)
        scenario = s.Scenario.model_validate(
            {
                "name": "Scenario",
                "createdBy": "Test",
                "startDate": "2030-01-01T00:00:00Z",
                "scenarioType": "Lunar",
                "elementTemplates": [
                    dict(self.vehicle, id=template_id, isp=320, maxFuel=100, fuel=fuel),
                    dict(
                        self.vehicle,
                        id=rover_id,
                        type="Surface Vehicle",
                        maxSpeed=10,
                        maxFuel=100,
                        fuel=fuel,
                    ),
                ],
                "instantiatedElements": [
                    {
                        "type": "Propulsive Vehicle",
                        "templateId": template_id,
                        "name": "A",
                    },
                    {
                        "type": "Propulsive Vehicle",
                        "templateId": template_id,
                        "name": "B",
                        "fuel": dict(self.fuel, amount=50),
                    },
                    {
                        "type": "Propulsive Vehicle",
                        "templateId": template_id,
                        "name": "C",
                        "isp": 350,
                        "maxFuel": 200,
                    },
                    {
                        "type": "Surface Vehicle",
                        "templateId": rover_id,
                        "name": "D",
                        "fuel": dict(self.fuel, amount=10),
                    },
                ],
            }
        )
        a, b, c, d = scenario.instantiated_elements
        self.assertIsNone(a.propulsion_systems)
        (system,) = b.propulsion_systems
        self.assertEqual((system.isp, system.fuel_tank.max_amount), (320, 100))
        self.assertEqual(system.fuel_tank.contents.amount, 50)
        (system,) = c.propulsion_systems
        self.assertEqual((system.isp, system.fuel_tank.max_amount), (350, 200))
        self.assertEqual(system.fuel_tank.contents.amount, 80)
        self.assertIsInstance(d, s.InstSurfaceVehicle)
        self.assertEqual(d.fuel_tank.max_amount, 100)
        self.assertEqual(d.fuel_tank.contents.amount, 10)

    def test_burn_type(self):
        burn = s.Burn(time=timedelta(0), delta_v=10)
        self.assertEqual(burn.type, s.PropulsionType.OMS)
        burn = s.Burn.model_validate({"time": "PT0S", "deltaV": 10, "type": "RCS"})
        self.assertEqual(burn.type, s.PropulsionType.RCS)
        with self.assertRaises(ValueError):
            s.Burn.model_validate({"time": "PT0S", "deltaV": 10, "type": "Ion"})


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
