import sys
import json
import unittest

if sys.version_info.major == 3:
    from unittest import mock
else:
    # Expect the `mock` package for python 2.
    # https://pypi.python.org/pypi/mock
    import mock


import os

from robot_status_cli.base import Client
from robot_status_cli.utils import get_token_generator, verify_token


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    headers = kwargs.get("headers")
    _t, token = headers["Authorization"].split(" ")
    data = args[1]
    try:
        verify_token("secret_key", json.dumps(data), token)
    except:
        return MockResponse(None, 401)

    return MockResponse(None, 201)

class TestClient(unittest.TestCase):

    def setUp(self):
        self.secret_key = "secret_key"
        self.data = {
            "var1": "1",
            "var:2": 1,
            "dict": {1:1}
        }

    def _generate_client(self):
        return Client(secret_key=self.secret_key,
                        server_url="")


    def test_token_generation(self):
        client = self._generate_client()
        token = client.generate_token(self.data)
        token_generator = get_token_generator(self.secret_key)
        str_data = json.dumps(self.data)
        self.assertEqual(
            token,
            token_generator.derive(str_data.encode()).hex()
        )

    @mock.patch('robot_status_cli.base.requests.post', side_effect=mocked_requests_post)
    def test_token_send_success(self, mock_request):
        client = self._generate_client()
        token = client.generate_token(self.data)
        response, status = client.send("", self.data, "test_key")
        self.assertEqual(response, True)
        self.assertEqual(status, None)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_token_send_failed(self, mock_request):
        client = self._generate_client()
        client._secret_key = "secret_key_2"
        response, status = client.send("", self.data, "test_key")
        self.assertEqual(response, False)
        self.assertEqual(status, 401)
