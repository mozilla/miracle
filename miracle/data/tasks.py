from miracle.config import TESTING
from miracle.data.delete import (
    DeleteUrls,
    DeleteUser,
)
from miracle.data.upload import upload_main
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


@celery_app.task(base=BaseTask, bind=True, queue='celery_delete')
def delete_urls(self, url_ids):
    return DeleteUrls(self)(url_ids)


@celery_app.task(base=BaseTask, bind=True, queue='celery_delete')
def delete(self, user):
    return DeleteUser(self)(user, delete_urls)


@celery_app.task(base=BaseTask, bind=True, queue='celery_upload')
def upload(self, user, payload, _upload_data=True):
    return upload_main(self, user, payload, _upload_data=_upload_data)
