from celery import Celery
import redis
import json
import time

app = Celery("tasks", broker="redis://broker//")

# Expire results quickly so that we don't fill up Redi's broker queue
app.conf.result_expires = 60

queue = redis.StrictRedis(host="broker", port=6379, db=0)
channel = queue.pubsub()


@app.task(bind=True)
def background_task(self, a, b):
    for tick in range(5):
        time.sleep(1)
        queue.publish("task:background_task:progress", json.dumps({"progress": tick}))
    return f"Found aliens on planet {a+b}!"
