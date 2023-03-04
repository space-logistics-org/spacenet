import unittest

from spacenet.schemas import ClassOfSupply, Environment, GenericResourceAmount, GenericResourceAmountRate


class TestGenericResourceAmount(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "class_of_supply": ClassOfSupply.COS_2,
            "environment": Environment.PRESSURIZED,
            "amount": 10.5
        }
        self.test_amount = GenericResourceAmount(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_amount.class_of_supply, self.test_data.get("class_of_supply"))
        self.assertEqual(self.test_amount.environment, self.test_data.get("environment"))
        self.assertEqual(self.test_amount.amount, self.test_data.get("amount"))


class TestGenericResourceAmountRate(unittest.TestCase):
    def setUp(self):
        self.test_data = {
            "class_of_supply": ClassOfSupply.COS_2,
            "environment": Environment.PRESSURIZED,
            "rate": 10.5
        }
        self.test_rate = GenericResourceAmountRate(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_rate.class_of_supply, self.test_data.get("class_of_supply"))
        self.assertEqual(self.test_rate.environment, self.test_data.get("environment"))
        self.assertEqual(self.test_rate.rate, self.test_data.get("rate"))