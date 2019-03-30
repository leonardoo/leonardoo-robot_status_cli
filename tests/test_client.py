import sys
import json
import unittest
from unittest import mock

import os

from robot_status_cli.base import get_token_generator, verify_token, generate_token
from robot_status_cli.client import Client


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


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    headers = kwargs.get("headers")
    _t, token = headers["Authorization"].split(" ")
    data = {"timestamp": headers["timestamp"]}
    try:
        verify_token("secret_key", json.dumps(data), token)
    except:
        return MockResponse(None, 401)
    return MockResponse(None, 200)


class TestClient(unittest.TestCase):

    def setUp(self):
        self.secret_key = "secret_key"
        self.data = {
            "var1": "1",
            "var:2": 1,
            "dict": {1: 1}
        }

    def _generate_client(self):
        return Client(secret_key=self.secret_key,
                      server_url="")

    def test_token_generation(self):
        token = generate_token(self.secret_key, self.data)
        token_generator = get_token_generator(self.secret_key)
        str_data = json.dumps(self.data)
        self.assertEqual(
            token,
            token_generator.derive(str_data.encode()).hex()
        )

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_token_send_post_success(self, mock_request):
        client = self._generate_client()
        response = client.post("", self.data, "test_key")
        self.assertEqual(response.status_code, 201)

    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_token_send_post_failed(self, mock_request):
        client = self._generate_client()
        client._secret_key = "secret_key_2"
        response = client.post("", self.data, "test_key")
        self.assertEqual(response.status_code, 401)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_token_send_get_success(self, mock_request):
        client = self._generate_client()
        response = client.get("", "test_key")
        self.assertEqual(response.status_code, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_token_send_get_failed(self, mock_request):
        client = self._generate_client()
        client._secret_key = "secret_key_2"
        response = client.get("", "test_key")
        self.assertEqual(response.status_code, 401)
