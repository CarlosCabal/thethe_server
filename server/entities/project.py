import json
import time

import bson

from server.db import DB
from server.entities.resource_types import ResourceType
from server.entities.update_central import UpdateCentral


class Projects:
    db = DB("projects")

    @staticmethod
    def create(name, user):
        if name == "" or not name.isalnum():
            raise ProjectNameException()

        project = Projects.db.collection.find_one({"name": name})
        if project:
            raise ProjectExistException()

        result = Projects.db.collection.insert_one(
            {
                "name": name,
                "createdby_ref": bson.ObjectId(user),
                "creation_date": time.time(),
                "last_open": time.time(),
                "resource_refs": [],  # { resource_id, resource_type }
            }
        )

        return result.inserted_id

    @staticmethod
    def delete(project_id):
        project_id = bson.ObjectId(project_id)
        Projects.db.collection.delete_one({"_id": project_id})

    @staticmethod
    def get_project_docs():
        return Projects.db.collection.find({})
        # return Projects.db.collection.find({"_id": {"$in": projects}})

    @staticmethod
    def search_resource_in_projects(resource_id):
        return Projects.db.collection.find(
            {"resource_refs.resource_id": resource_id}, {"_id": 1, "name": 1}
        )


class Project:
    def __init__(self, project_id):
        self.db = Projects.db
        self.project_id = bson.ObjectId(project_id)

    def get_id(self):
        return str(self.project_id)

    def remove_resource(self, resource_id):
        self.db.collection.find_one_and_update(
            {"_id": self.project_id},
            {"$pull": {"resource_refs": {"resource_id": resource_id}}},
        )

    def rename(self, new_name):
        if len(list(self.db.collection.find({"name": new_name}))) > 0:
            return False

        self.db.collection.find_one_and_update(
            {"_id": self.project_id}, {"$set": {"name": new_name}},
        )

        return True

    def set_open_timestamp(self):
        self.db.collection.find_one_and_update(
            {"_id": self.project_id}, {"$set": {"last_open": time.time()}}
        )

    def add_resource(self, resource):
        data = {
            "resource_id": resource.resource_id,
            "resource_type": resource.get_type_value(),
        }

        self.db.collection.find_one_and_update(
            {"_id": self.project_id}, {"$addToSet": {"resource_refs": data}}
        )

    def get_resource(self, resource_id):
        return self.db.collection.find_one(
            {"_id": self.project_id, "resource_refs.resource_id": resource_id},
            {"resource_refs": 1},
        )

    def get_resources(self):
        result = self.db.collection.find_one(
            {"_id": self.project_id,}, {"resource_refs": 1},
        )

        if result and "resource_refs" in result.keys():
            return [item["resource_id"] for item in result["resource_refs"]]
        else:
            return []

    def get_updates(self, timestamp):
        return UpdateCentral().get_pending_updates(self.project_id, timestamp)


class ProjectExistException(BaseException):
    pass


class ProjectNameException(BaseException):
    pass


class ProjectNotExistsException(BaseException):
    pass
