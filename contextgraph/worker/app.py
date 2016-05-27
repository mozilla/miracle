from celery import Celery
from celery.app import app_or_default
from celery.signals import (
    worker_process_init,
    worker_process_shutdown,
)
from kombu import Queue

from contextgraph.config import REDIS_URI


CELERY_QUEUES = (
    Queue('celery_default', routing_key='celery_default'),
)  #: List of :class:`kombu.Queue` instances.


def configure_celery(celery_app):
    celery_app.config_from_object('contextgraph.worker.settings')
    celery_app.conf.update(
        BROKER_URL=REDIS_URI,
        CELERY_RESULT_BACKEND=REDIS_URI,
        CELERY_QUEUES=CELERY_QUEUES,
    )


def init_worker(celery_app):
    celery_app.redis_client = None


def shutdown_worker(celery_app):
    del celery_app.redis_client


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


celery_app = Celery('contextgraph.worker.app')
configure_celery(celery_app)
