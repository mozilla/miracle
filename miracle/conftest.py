import gc
import warnings

import pytest
import webtest

from miracle.bucket import create_bucket
from miracle.cache import create_cache
from miracle.crypto import create_crypto
from miracle.kinesis import create_kinesis
from miracle.log import (
    create_raven,
    create_stats,
)
from miracle.web.app import (
    create_app,
    shutdown_app,
)
from miracle.worker.app import (
    celery_app,
    init_worker,
    shutdown_worker,
)


@pytest.fixture(scope='session', autouse=True)
def package():
    # Apply gevent monkey patches as early as possible during tests.
    from gevent.monkey import patch_all
    patch_all()

    # Enable all warnings in test mode.
    warnings.resetwarnings()
    warnings.simplefilter('default')

    # Look for memory leaks.
    gc.set_debug(gc.DEBUG_UNCOLLECTABLE)

    yield None

    # Print memory leaks.
    if gc.garbage:  # pragma: no cover
        print('Uncollectable objects found:')
        for obj in gc.garbage:
            print(obj)


@pytest.fixture(scope='session')
def global_bucket():
    bucket = create_bucket()
    bucket.clear()
    yield bucket
    bucket.close()


@pytest.fixture(scope='function')
def bucket(global_bucket):
    yield global_bucket
    global_bucket.clear()


@pytest.fixture(scope='session')
def global_cache():
    cache = create_cache()
    yield cache
    cache.close()


@pytest.fixture(scope='function')
def cache(global_cache):
    yield global_cache
    global_cache.flushdb()


@pytest.fixture(scope='session')
def crypto():
    crypto = create_crypto()
    yield crypto


@pytest.fixture(scope='session')
def global_kinesis():
    kinesis = create_kinesis()
    kinesis.clear()
    yield kinesis
    kinesis.close()


@pytest.fixture(scope='function')
def kinesis(global_kinesis):
    yield global_kinesis
    global_kinesis.clear()


@pytest.fixture(scope='session')
def global_raven():
    raven = create_raven()
    yield raven


@pytest.fixture(scope='function')
def raven(global_raven):
    yield global_raven
    messages = [msg['message'] for msg in global_raven.msgs]
    global_raven.clear()
    assert not messages


@pytest.fixture(scope='session')
def global_stats():
    stats = create_stats()
    yield stats
    stats.close()


@pytest.fixture(scope='function')
def stats(global_stats):
    yield global_stats
    global_stats.clear()


@pytest.fixture(scope='session')
def global_celery(crypto, global_bucket, global_cache,
                  global_raven, global_stats):
    init_worker(
        celery_app,
        _bucket=global_bucket,
        _cache=global_cache,
        _crypto=crypto,
        _raven=global_raven,
        _stats=global_stats)
    yield celery_app
    shutdown_worker(celery_app)


@pytest.fixture(scope='function')
def celery(global_celery, bucket, cache, raven, stats):
    yield global_celery


@pytest.fixture(scope='session')
def global_app(crypto, global_cache, global_celery, global_kinesis,
               global_raven, global_stats):
    wsgiapp = create_app(
        _cache=global_cache,
        _crypto=crypto,
        _kinesis=global_kinesis,
        _raven=global_raven,
        _stats=global_stats)
    app = webtest.TestApp(wsgiapp)
    yield app
    shutdown_app(app.app)


@pytest.fixture(scope='function')
def app(global_app, cache, celery, kinesis, raven, stats):
    yield global_app
