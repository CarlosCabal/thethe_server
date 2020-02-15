# TODO: Untested plugin. Disabled
import json
import traceback

from server.entities.plugin_manager import PluginManager
from server.entities.resource_types import ResourceType
from server.entities.resource_manager import ResourceManager
from server.entities.plugin_result_types import PluginResultStatus

from tasks.tasks import celery_app
import json
import requests


# Which resources are this plugin able to work with
RESOURCE_TARGET = [ResourceType.DOMAIN]

# Plugin Metadata {a description, if target is actively reached and name}
PLUGIN_AUTOSTART = False
PLUGIN_DESCRIPTION = "List Threats for domain"
PLUGIN_DISABLE = True
PLUGIN_IS_ACTIVE = False
PLUGIN_NAME = "threatminer"
PLUGIN_NEEDS_API_KEY = False

# IMPORTANT NOTE: Please note that the rate limit is set to 10 queries per minute.
API_KEY = False
API_KEY_IN_DDBB = False
API_KEY_DOC = ""
API_KEY_NAMES = []


class Plugin:
    def __init__(self, resource, project_id):
        self.project_id = project_id
        self.resource = resource

    def do(self):
        resource_type = self.resource.get_type()

        try:
            if resource_type == ResourceType.DOMAIN:
                to_task = {
                    "domain": self.resource.get_data()["domain"],
                    "resource_id": self.resource.get_id_as_string(),
                    "project_id": self.project_id,
                    "resource_type": resource_type.value,
                    "plugin_name": PLUGIN_NAME,
                }
                threatminer_task.delay(**to_task)

        except Exception as e:
            tb1 = traceback.TracebackException.from_exception(e)
            print("".join(tb1.format()))


def threatminer_searchAPTNotes(fulltext):
    try:
        URL = "https://api.threatminer.org/v2/reports.php?q={fulltext}&rt=1"
        response = {}
        response = requests.get(URL.format(**{"fulltext": fulltext}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_APTNotesToIoCs(filename_param, year):
    try:
        URL = (
            "https://api.threatminer.org/v2/report.php?q={filename_param}&y={year}&rt=1"
        )
        response = {}

        response = requests.get(
            URL.format(**{"filename_param": filename_param, "year": year})
        )
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_AVDetection(name_virus):
    try:
        URL = "	https://api.threatminer.org/v2/av.php?q={name_virus}&rt=1"
        response = {}

        response = requests.get(URL.format(**{"name_virus": name_virus}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_ip(ip, tab_rt):
    try:
        URL = "https://api.threatminer.org/v2/host.php?q={ip}&rt={tab_rt}"
        response = {}

        response = requests.get(URL.format(**{"ip": ip, "tab_rt": tab_rt}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_domain(domain, tab_rt):
    try:
        URL = "https://api.threatminer.org/v2/domain.php?q={domain}&rt={tab_rt}"
        response = {}

        response = requests.get(URL.format(**{"domain": domain, "tab_rt": tab_rt}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_samples(hash, tab_rt):
    try:
        URL = "https://api.threatminer.org/v2/sample.php?q={hash}}&rt={tab_rt}"
        response = {}

        response = requests.get(URL.format(**{"hash": hash, "tab_rt": tab_rt}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


def threatminer_ssl(hash, tab_rt):
    try:
        URL = "https://api.threatminer.org/v2/ssl.php?q={hash}&rt={tab_rt}"
        response = {}

        response = requests.get(URL.format(**{"hash": hash, "tab_rt": tab_rt}))
        if not response.status_code == 200:
            print("API key error!")
            return None
        else:
            response = json.loads(response.content)

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


@celery_app.task
def threatminer_task(plugin_name, project_id, resource_id, resource_type, domain):
    try:
        resource_type = ResourceType(resource_type)
        if resource_type == ResourceType.DOMAIN:
            query_result = threatminer_domain(domain, "1")
        else:
            print("threatminer resource type does not found")

        PluginManager.set_plugin_results(
            resource_id, plugin_name, project_id, query_result, result_status
        )

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
