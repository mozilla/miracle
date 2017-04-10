from miracle.config import TESTING
from miracle.data.upload import Upload
from miracle.worker.app import celery_app
from miracle.worker.task import BaseTask


if TESTING:
    @celery_app.task(base=BaseTask, bind=True, queue='celery_default')
    def error(self, value):
        raise ValueError(value)


@celery_app.task(base=BaseTask, bind=True, queue='celery_upload')
def upload(self, sequence_number=None, shard_id=None):
    return Upload(self)(
        sequence_number=sequence_number,
        shard_id=shard_id,
    )
