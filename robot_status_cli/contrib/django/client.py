
from robot_status_cli.base import Client as BaseClient
from django.conf import settings


class DjangoClient(BaseClient):

    def __init__(self):
        super(DjangoClient, self).__init__(settings.CLI_SETTINGS["secret_key"],
                                           settings.CLI_SETTINGS["server_url"])
        self.client_settings = settings.CLI_SETTINGS
        self._set_api_urls(self.client_settings["endpoints"])

    def _set_api_urls(self, endpoints):
        self.endpoints = {}
        for project in endpoints.keys():
            self.endpoints[project] = endpoints[project]

    def get_endpoint_by_project(self, project):
        if project in self.endpoints:
            return self.endpoints[project]
        return ""

    def send_data(self, project, data):
        url_project = self.get_endpoint_by_project(project)
        url = self.server_url + url_project
        url_list = url.split("//")
        url = ""
        url = url_list.pop(0) + "//" + url_list.pop(0)
        for index, url_splited in enumerate(url_list):
            url = "{0}/{1}".format(url, url_splited)
        return self.send(url, data, self.client_settings["public_key"])
