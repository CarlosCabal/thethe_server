import time
import bson
import json
import traceback
import urllib.parse


from flask import Blueprint, request, abort, jsonify

from server.utils.password import token_required

from server.entities.resource_manager import ResourceManager

from server.entities.resource_types import ResourceType, ResourceTypeException
from server.entities.user import User
from server.entities.project import Project

resources_api = Blueprint("resources", __name__)


@resources_api.route("/api/create_resource", methods=["POST"])
@token_required
def create_resource(user):
    try:
        resource_name = request.json["resource_name"].strip()
        resource_type = request.json["resource_type"].lower()

        resource_type = ResourceType.get_type_from_string(resource_type)

        resource, created = ResourceManager.get_or_create(resource_name, resource_type)

        project = User(user).get_active_project()
        project.add_resource(resource)

        response = []
        response.append(resource.to_JSON())

        if created:
            resource.launch_plugins(project.get_id())

        # Deal with the case of URL resources where we have the chance to add a Domain or IP
        if resource.get_type() == ResourceType.URL:
            ip_or_domain = urllib.parse.urlparse(resource_name).netloc
            resource_type = ResourceType.validate_ip_or_domain(ip_or_domain)
            if ip_or_domain:
                resource, created = ResourceManager.get_or_create(
                    ip_or_domain, resource_type
                )
                project.add_resource(resource)
                response.append(
                    {
                        "success_message": f"Added new resource: {ip_or_domain}",
                        "new_resource": resource.to_JSON(),
                        "type": resource.get_type_value(),
                    }
                )
                if created:
                    resource.launch_plugins(project.get_id())

        # TODO: Deal with the case of domain -> IP
        # TODO: Deal with the case of emails -> domains -> IP

        return jsonify(response)

    except ResourceTypeException:
        return jsonify({"error_message": "Trying to add an unknown resource type"}), 400

    except Exception as e:
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return jsonify({"error_message": "Server error :("}), 400


@resources_api.route("/api/get_resources", methods=["POST"])
@token_required
def get_resources(user):
    try:
        project_id = request.json["project_id"]
        user_projects = [str(project) for project in User(user).get_projects()]

        # User unable to load the project
        if not project_id in user_projects:
            return (
                jsonify(
                    {
                        "error_message": f"User is not allowed to load project {project_id}"
                    }
                ),
                400,
            )

        project = Project(project_id)
        resources = project.get_resources()

        results = []
        for resource in resources:
            results.append(ResourceManager.get(resource).resource_json())

        return jsonify(results)

    except Exception as e:
        print(f"Error getting resource list {e}")
        tb1 = traceback.TracebackException.from_exception(e)
        print("".join(tb1.format()))
        return jsonify({"error_message": "Error getting resources"}), 400


@resources_api.route("/api/unlink_resource", methods=["POST"])
@token_required
def unlink_resource(user):
    """
        Unlink (not remove) a resource from the active project.
    """
    try:
        resource_id = bson.ObjectId(request.json["resource_id"])

        project = User(user).get_active_project()
        project.remove_resource(resource_id)

        return jsonify({"success_message": "Resource unlinked from project"})

    except Exception as e:
        print(e)
        return jsonify({"error_message": "Error unlinking resource from project"}), 400


@resources_api.route("/api/get_resource", methods=["POST"])
@token_required
def get_resource(user):
    """
        Return a resource json dump by its ID
    """

    resource_id = request.json["resource_id"]

    try:
        resource = ResourceManager.get(resource_id)
        if resource:
            return jsonify(resource.to_JSON())
        else:
            return jsonify({"error_message": "Resource not found"})

    except ValueError:
        raise ResourceTypeException()

    except ResourceTypeException:
        return jsonify({"error_message": "Received an unknown type of resource"}), 400

    except Exception as e:
        print(f"Error getting ip list {e}")
        return jsonify({"error_message": "Error getting resources"}), 400


@resources_api.route("/api/get_lazy_plugin_results", methods=["POST"])
@token_required
def get_lazy_plugin_results(user):
    """
        Return a resource but with a plugin selected history snapshot
    """

    resource_id = request.json["params"]["resource_id"]
    plugin_name = request.json["params"]["plugin_name"]

    if "timestamp_index" in request.json["params"]:
        timestamp_index = request.json["params"]["timestamp_index"]
    else:
        timestamp_index = 0

    try:
        resource = ResourceManager.get(resource_id)
        if resource:
            return jsonify(resource.to_JSON(timestamp_index=timestamp_index))
        else:
            return jsonify({"error_message": "Resource not found"})

    except ValueError:
        raise ResourceTypeException()

    except ResourceTypeException:
        return jsonify({"error_message": "Received an unknown type of resource"}), 400

    except Exception as e:
        print(f"Error getting ip list {e}")
        return jsonify({"error_message": "Error getting resources"}), 400


@resources_api.route("/api/get_full_resource", methods=["POST"])
@token_required
def get_full_resource(user):
    """
        Return a resource with all its results
    """

    resource_id = request.json["resource_id"]

    try:
        resource = ResourceManager.get(resource_id)
        if resource:
            return jsonify(resource.to_JSON())
        else:
            return jsonify({"error_message": "Resource not found"})

    except ValueError:
        raise ResourceTypeException()

    except ResourceTypeException:
        return jsonify({"error_message": "Received an unknown type of resource"}), 400

    except Exception as e:
        print(f"Error getting ip list {e}")
        return jsonify({"error_message": "Error getting resources"}), 400
