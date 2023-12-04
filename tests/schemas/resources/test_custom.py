import unittest
from uuid import uuid4

from spacenet.schemas import (
    ClassOfSupply,
    Environment,
    ResourceAmount,
    ResourceAmountRate,
)


class TestResourceAmount(unittest.TestCase):
    def setUp(self):
        self.test_data = {"resource": uuid4(), "amount": 10.5}
        self.test_amount = ResourceAmount(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_amount.resource, self.test_data.get("resource"))
        self.assertEqual(self.test_amount.amount, self.test_data.get("amount"))


class TestResourceAmountRate(unittest.TestCase):
    def setUp(self):
        self.test_data = {"resource": uuid4(), "rate": 10.5}
        self.test_rate = ResourceAmountRate(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_rate.resource, self.test_data.get("resource"))
        self.assertEqual(self.test_rate.rate, self.test_data.get("rate"))
