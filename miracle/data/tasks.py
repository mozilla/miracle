from miracle.config import TESTING
from miracle.data.delete import main as delete_main
from miracle.data.upload import main as upload_main
from miracle.worker.app import celery_app
from miracle.worker.task import BaseTask


if TESTING:
    @celery_app.task(base=BaseTask, bind=True, queue='celery_default')
    def dummy(self):
        self.cache.incr('foo', 2)
        return int(self.cache.get('foo'))

    @celery_app.task(base=BaseTask, bind=True, queue='celery_default')
    def error(self, value):
        raise ValueError(value)


@celery_app.task(base=BaseTask, bind=True, queue='celery_default')
def delete(self, user, _delete_data=True):
    return delete_main(self, user, _delete_data=_delete_data)


@celery_app.task(base=BaseTask, bind=True, queue='celery_default')
def upload(self, user, payload, _upload_data=True):
    return upload_main(self, user, payload, _upload_data=_upload_data)
