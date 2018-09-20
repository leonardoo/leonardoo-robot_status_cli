
import json

import requests

from .utils import get_token_generator


class Client:

    def __init__(self, secret_key, server_url):
        self._secret_key = secret_key
        self.server_url = server_url

    @property
    def token_generator(self):
        return get_token_generator(self._secret_key)

    def send(self, url, data, public_key):
        token = "bearer {}".format(self.generate_token(data))
        response = requests.post(url,
                                 data,
                                 headers={'Authorization': token,
                                          'public_key': public_key})
        if response.status_code == 201:
            return True, None
        else:
            return False, response.status_code

    def generate_token(self, data):
        str_data = json.dumps(data)
        return self.token_generator.derive(str_data.encode()).hex()
