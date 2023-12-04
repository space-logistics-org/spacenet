import unittest
from uuid import uuid4
from datetime import timedelta

from spacenet.schemas import Burn


class TestBurn(unittest.TestCase):
    def setUp(self):
        self.test_data = {"time": timedelta(hours=1), "delta_v": 100}
        self.test_burn = Burn(**self.test_data)

    def test_good_data(self):
        self.assertEqual(self.test_burn.time, self.test_data.get("time"))
        self.assertEqual(self.test_burn.delta_v, self.test_data.get("delta_v"))
