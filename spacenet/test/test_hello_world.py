import unittest
import json
import pkg_resources
import pytest

from spacenet.schemas.hello_world import HelloWorld
from pydantic import ValidationError

pytestmark = [pytest.mark.unit]


class TestHelloWorld(unittest.TestCase):

    def test_good_data(self):
        good_data = {"message": "Hello World"}
        hello = HelloWorld(**good_data)
        self.assertEqual(hello.message, good_data.get("message"))

    def test_bad_data_missing_message(self):
        bad_data = {"contents": "Hello World"}
        with self.assertRaises(ValidationError):
            hello = HelloWorld(**bad_data)

    def test_bad_data_message_type(self):
        bad_data = {"message": ["Hello World"]}
        with self.assertRaises(ValidationError):
            hello = HelloWorld(**bad_data)

    def test_good_example_data(self):
        messages = json.loads(
            pkg_resources.resource_string(
                __name__,
                'hello_world_data.json'
            )
        )
        for message in messages.get('good_data'):
            hello = HelloWorld.parse_obj(message)

    def test_bad_example_data(self):
        messages = json.loads(
            pkg_resources.resource_string(
                __name__,
                'hello_world_data.json'
            )
        )
        for message in messages.get('bad_data'):
            with self.assertRaises(ValidationError):
                hello = HelloWorld.parse_obj(message)
