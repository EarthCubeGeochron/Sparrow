from celery import Celery
import time

app = Celery("tasks", broker="redis://broker//")


@app.task(bind=True)
def background_task(self, a, b):
    for tick in range(5):
        time.sleep(1)
        self.update_state(state="PROGRESS", meta={"progress": 100})
        return f"Hello, planet {a+b}!"
