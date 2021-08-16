# import json
# import unittest

# import pkg_resources
# import pytest
# from pydantic import ValidationError

# from spacenet.schemas.scenario import (
    # Manifest,
    # Network,
    # ScenarioType,
    # Scenario,
)

# pytestmark = [pytest.mark.unit, pytest.mark.resource, pytest.mark.schema]


# class TestFromFile(unittest.TestCase):

    # good_scenario = json.loads(
        # pkg_resources.resource_string(test.__name__, "good_scenario.json")
    )

    # bad_scenario = json.loads(
        # pkg_resources.resource_string(test.__name__, "bad_scenario.json")
    )

    # good_network = json.loads(
        # pkg_resources.resource_string(test.__name__, "good_network.json")
    )

    # bad_network = json.loads(
        # pkg_resources.resource_string(test.__name__, "bad_network.json")
    )

    # def test_Scenario(self):

        # for scenario in self.good_scenario:
            # testScenario = Scenario.parse_obj(scenario)
            # self.assertEqual(testScenario.name, scenario.get("name"))
            # self.assertEqual(testScenario.startDate, scenario.get("startDate"))
            # self.assertEqual(testScenario.scenarioType, scenario.get("scenarioType"))
            # self.assertEqual(testScenario.network, scenario.get("network"))
            # self.assertEqual(testScenario.missionList, scenario.get("missionList"))
            # self.assertEqual(testScenario.elementList, scenario.get("elementList"))
            # self.assertEqual(testScenario.manifest, scenario.get("manifest"))
            # self.assertEqual(testScenario.volumeConstrained, scenario.get("volumeConstrained"))
            # self.assertEqual(testScenario.environmentConstrained, scenario.get("environmentConstrained"))

    # def test_bad_Scenario(self):
        # for scenario in self.bad_scenario:
            # with self.assertRaises(ValidationError):
                # bad_scenario = Scenario.pasre_obj(scenario)
