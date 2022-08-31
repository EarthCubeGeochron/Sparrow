from celery import Celery
from celery.signals import after_setup_logger
from macrostrat.utils import setup_stderr_logs
import sparrow
import redis
import json
import time

_app = sparrow.core.get_app()
_app.setup_database()

app = _app.plugins.get("task-manager").celery


queue = redis.StrictRedis(host="broker", port=6379, db=0)
channel = queue.pubsub()


@app.task(bind=True, name="background-task")
def background_task(self):
    for tick in range(5):
        time.sleep(1)
        print("Hello, world")
        queue.publish("task:background_task", json.dumps({"progress": tick}))
    queue.publish("task:background_task", json.dumps({"success": True}))
    return True


# celery = Celery("tasks", broker="redis://broker//")

# # Expire results quickly so that we don't fill up Redi's broker queue
# celery.conf.result_expires = 60


# @after_setup_logger.connect()
# def logger_setup_handler(logger, **kwargs):
#     setup_stderr_logs("sparrow_worker", "sparrow", "celery.task")


# @celery.task()
# def import_task(name):
#     from sparrow.context import get_sparrow_app

#     app = get_sparrow_app()

#     try:
#         plugin = app.plugins.get("import-tracker")
#         if plugin is None:
#             raise Exception("Could not find plugin")
#         pipeline = plugin.pipelines.get(name, None)
#         if pipeline is None:
#             raise Exception("Could not find task named " + name)
#         queue.publish("sparrow:task:" + name, json.dumps({"text": "Starting task"}))
#         pipeline.message_queue = queue
#         pipeline.run_task()
#     except Exception as exc:
#         queue.publish("sparrow:task:" + name, json.dumps({"text": str(exc)}))
#         raise exc
