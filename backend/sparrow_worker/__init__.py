from celery import Celery
import redis
import json
import time

celery = Celery("tasks", broker="redis://broker//")

# Expire results quickly so that we don't fill up Redi's broker queue
celery.conf.result_expires = 60

queue = redis.StrictRedis(host="broker", port=6379, db=0)
channel = queue.pubsub()


@celery.task(bind=True)
def background_task(self, a, b):
    for tick in range(5):
        time.sleep(1)
        queue.publish("task:background_task", json.dumps({"progress": tick}))
    queue.publish("task:background_task", json.dumps({"success": True}))


@celery.task()
def import_task(name):
    from sparrow.context import get_sparrow_app

    app = get_sparrow_app()
    plugin = app.plugins.get("import-tracker")
    if plugin is None:
        return
    pipeline = plugin.pipelines.get(name, None)
    if pipeline is None:
        return
    pipeline.message_queue = queue
    pipeline.import_all()
