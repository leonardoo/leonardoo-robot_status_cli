
import json

import requests

from .utils import get_token_generator
from .compat import get_str_to_hex


class Client(object):

    def __init__(self, secret_key, server_url):
        self._secret_key = secret_key
        self.server_url = server_url

    @property
    def token_generator(self):
        return get_token_generator(self._secret_key)

    def send(self, url, data, public_key):
        token = "bearer {}".format(self.generate_token(data))
        try:
            response = requests.post(url,
                                     data,
                                     headers={'Authorization': token,
                                              'public_key': public_key},
                                     timeout=10)
            if response.status_code == 201:
                return True, None
            else:
                return False, response.status_code
        except Exception as e:
            return False, None

    def generate_token(self, data):
        str_data = json.dumps(data)
        return get_str_to_hex(self.token_generator.derive(str_data.encode()))
