from contextgraph.worker.app import celery_app
from contextgraph.worker.task import BaseTask


@celery_app.task(base=BaseTask, bind=True, queue='celery_default')
def dummy(self):
    return True
