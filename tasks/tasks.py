import os

from celery import Celery

# TODO: Integrar en una sola funcion, se repeite en plugins.py
EXCLUDE_SET = ["__init__.py", "TEMPLATE.py"]

plugins = []
for root, dirs, files in os.walk("server/plugins"):
    for file in files:
        if ".py" in file[-3:] and not file in EXCLUDE_SET:
            plugins.append("server.plugins.{}".format(os.path.splitext(file)[0]))

celery_app = Celery(
    "tasks", backend="redis://redis", broker="redis://redis:6379/0", include=plugins,
)
