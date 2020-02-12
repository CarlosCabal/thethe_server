# TODO: needs heavy testing before enabling

import traceback
from server.entities.resource_types import ResourceType

from tasks.tasks import celery_app
from server.entities.plugin_result_types import PluginResultStatus
from server.entities.resource_base import Resource


# Login with the following information:
# Login Name: zigineki@getnada.com
# Password: 6aiIRgAm
# The BotScout Team
# http://BotScout.com

import json
import urllib.request
from bs4 import BeautifulSoup
from server.entities.resource_base import Resource

from server.entities.resource_manager import ResourceManager

from tasks.api_keys import KeyRing

API_KEY = KeyRing().get("botscout")

# Which resources are this plugin able to work with
RESOURCE_TARGET = [ResourceType.IPv4]

# Plugin Metadata {a description, if target is actively reached and name}
PLUGIN_AUTOSTART = False
PLUGIN_DESCRIPTION = "BotScout helps prevent automated web scripts, known as 'bots', from multiples sources"
PLUGIN_DISABLE = True
PLUGIN_IS_ACTIVE = False
PLUGIN_NAME = "botscout"
PLUGIN_NEEDS_API_KEY = True

API_KEY = KeyRing().get("botscout")
API_KEY_IN_DDBB = bool(API_KEY)
API_KEY_DOC = "https://botscout.com/getkey.htm"
API_KEY_NAMES = ["botscout"]


class Plugin:
    def __init__(self, resource, project_id):
        self.project_id = project_id
        self.resource = resource

    def do(self):
        resource_type = self.resource.get_type()

        try:
            to_task = {
                "ip": self.resource.get_data()["address"],
                "resource_id": self.resource.get_id_as_string(),
                "project_id": self.project_id,
                "resource_type": resource_type.value,
                "plugin_name": PLUGIN_NAME,
            }
            botscout.delay(**to_task)

        except Exception as e:
            tb1 = traceback.TracebackException.from_exception(e)
            print("".join(tb1.format()))


def botscout_ip(ip):
    try:
        API_KEY = KeyRing().get("botscout")
        if not API_KEY:
            print("No API key...!")
            return None

        URL = f"http://botscout.com/test/?ip={ip}&key={API_KEY}&format=xml"
        response = urllib.request.urlopen(URL).read()
        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


# parsing results
def botscout_ip_details(ip):
    try:
        URL = f"http://botscout.com/search.htm?sterm={ip}&stype=q"
        response = urllib.request.urlopen(URL).read()

        # parser HTML to extract last or To 10
        # soup = BeautifulSoup(response, 'html.parser')
        # html_data = soup.find('table', attrs={'class':'sortable'})
        # table_data = [[cell.text for cell in row("td")]]
        #                         for row in soup.body.find_all('table', attrs={'class' : 'sortable'})]

        # print(json.dumps(dict(table_data)))

        return response

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return None


@celery_app.task
def botscout_task(plugin_name, project_id, resource_id, resource_type, ip):
    try:
        resource_type = ResourceType(resource_type)
        if resource_type == ResourceType.DOMAIN:
            query_result = botscout_ip(ip)
        else:
            print("BotScout resource type does not found")

        resource = ResourceManager.get(resource_id)
        resource.set_plugin_results(
            plugin_name, project_id, resource_id, resource_type, query_result
        )

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
