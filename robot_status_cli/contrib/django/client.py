from typing import Dict, Any

from robot_status_cli.base import Client as BaseClient
from django.conf import settings


class DjangoClient(BaseClient):

    def __init__(self):
        super().__init__(settings.CLI_SETTINGS["secret_key"],
                         settings.CLI_SETTINGS["server_url"])
        self.client_settings = settings.CLI_SETTINGS
        self.set_api_urls(self.client_settings["endpoints"])

    def _set_api_urls(self, endpoints: Dict[Any, Any]):
        self.endpoints = {project: url for project, url in endpoints}

    def get_endpoint_by_project(self, project: str):
        return self.endpoints[project]

    def send_data(self, project: str, data: Dict[Any, Any]):
        url = self.server_url + self.get_endpoint_by_project(project)
        return self.send(url, data, self.client_settings["public_key"])
