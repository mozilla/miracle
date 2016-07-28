from celery import Celery
from celery.app import app_or_default
from celery.signals import (
    worker_process_init,
    worker_process_shutdown,
)
from kombu import Queue

from miracle.bucket import create_bucket
from miracle.cache import create_cache
from miracle.db import create_db
from miracle.config import REDIS_URI
from miracle.log import (
    configure_logging,
    create_raven,
    create_stats,
)


CELERY_QUEUES = (
    Queue('celery_default', routing_key='celery_default'),
    Queue('celery_delete', routing_key='celery_delete'),
    Queue('celery_upload', routing_key='celery_upload'),
)


def configure_celery(celery_app):
    celery_app.config_from_object('miracle.worker.settings')
    celery_app.conf.update(
        BROKER_URL=REDIS_URI,
        CELERY_RESULT_BACKEND=REDIS_URI,
        CELERY_QUEUES=CELERY_QUEUES,
    )


def init_worker(celery_app,
                _bucket=None, _cache=None, _db=None, _raven=None, _stats=None):
    configure_logging()

    celery_app.bucket = create_bucket(_bucket=_bucket)
    celery_app.cache = create_cache(_cache=_cache)
    celery_app.db = create_db(_db=_db)
    celery_app.raven = create_raven(transport='threaded', _raven=_raven)
    celery_app.stats = create_stats(_stats=_stats)

    celery_app.bucket.connect(celery_app.raven)
    celery_app.cache.ping(celery_app.raven)
    celery_app.db.ping(celery_app.raven)


def shutdown_worker(celery_app):
    del celery_app.bucket
    celery_app.cache.close()
    del celery_app.cache
    celery_app.db.close()
    del celery_app.db
    del celery_app.raven
    celery_app.stats.close()
    del celery_app.stats


@worker_process_init.connect
def init_worker_process(signal, sender, **kw):  # pragma: no cover
    # get the app in the current forked worker process
    celery_app = app_or_default()
    init_worker(celery_app)


@worker_process_shutdown.connect
def shutdown_worker_process(signal, sender, **kw):  # pragma: no cover
    # get the app in the current forked worker process
    celery_app = app_or_default()
    shutdown_worker(celery_app)


celery_app = Celery('miracle.worker.app')
configure_celery(celery_app)
