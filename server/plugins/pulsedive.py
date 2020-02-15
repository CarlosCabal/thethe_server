# TODO: Plugin pending of testing

import traceback
import json
import requests, base64

from tasks.api_keys import KeyRing
from server.entities.resource_manager import ResourceManager
from server.entities.plugin_manager import PluginManager
from server.entities.resource_types import ResourceType
from tasks.tasks import celery_app
from server.entities.plugin_result_types import PluginResultStatus

RESOURCE_TARGET = []

# Plugin Metadata {a description, if target is actively reached and name}
PLUGIN_AUTOSTART = False
PLUGIN_DESCRIPTION = ""
PLUGIN_DISABLE = True
PLUGIN_IS_ACTIVE = False
PLUGIN_NAME = "pulsedive"
PLUGIN_NEEDS_API_KEY = True

API_KEY = KeyRing().get("pulsedive")
API_KEY_IN_DDBB = bool(API_KEY)
API_KEY_DOC = ""
API_KEY_NAMES = ["pulsedive"]

PLUGIN_NEEDS_API_KEY = True
URL = "https://pulsedive.com/api/analyze.php"
URL_INFO = "https://pulsedive.com/api/info.php"

## Indicator(https://pulsedive.com/api/?q=indicators)
## param = domain, md5, sha1, sha256
## Function OK
def pulsedive_get_ioc_byvalue(param):
    try:
        API_KEY = KeyRing().get("pulsedive")
        if not API_KEY:
            print("No API key...!")
            return None

        response = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"
        }

        params = f"?pretty=1&key={API_KEY}&indicator={param}"

        response = requests.get(URL_INFO, params=params, headers=headers)
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


print(pulsedive_get_ioc_byvalue("com1.ru"))


## Make submit but never show results
# {'success': 'Added indicator to queue.', 'qid': 98643406}
# {'success': 'Added indicator to queue.', 'qid': 98643407}
def pulsedive_analyze(domain):
    try:
        API_KEY = KeyRing().get("pulsedive")
        if not API_KEY:
            print("No API key...!")
            return None

        pyb64_domain = base64.b64encode(bytes(domain, "utf-8"))

        response = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        post_data = {
            "ioc": pyb64_domain.decode("utf-8"),
            "probe": "1",
            "pretty": "1",
            "app_key": API_KEY,
        }

        response = requests.post(URL, post_data, headers=headers)
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


# In progress. API response ok but results not found always. Review!
def pulsedive_getreport(qid):
    try:
        API_KEY = KeyRing().get("pulsedive")
        if not API_KEY:
            print("No API key...!")
            return None

        response = {}

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"
        }

        params = f"?pretty=1&key={API_KEY}&qid={qid}"

        response = requests.get(URL, params=params, headers=headers)
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
def pulsedive_task(plugin_name, project_id, resource_id, resource_type, domain_or_hash):
    try:
        resource_type = ResourceType(resource_type)
        if resource_type == ResourceType.DOMAIN or resource_type == ResourceType.HASH:
            query_result = pulsedive_get_ioc_byvalue(domain_or_hash)
        else:
            print("PulseDive resource type does not found")

        resource = ResourceManager.get(resource_id, resource_type)
        resource.set_plugin_results(
            plugin_name, project_id, resource_id, resource_type, query_result
        )

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
