import gc
import warnings

import pytest
import webtest

from contextgraph.web.app import (
    create_app,
    shutdown_app,
)
from contextgraph.worker.app import (
    celery_app,
    init_worker,
    shutdown_worker,
)


@pytest.yield_fixture(scope='session', autouse=True)
def package():
    # Apply gevent monkey patches as early as possible during tests.
    from gevent import monkey
    monkey.patch_all()

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


@pytest.yield_fixture(scope='session')
def global_app():
    wsgiapp = create_app()
    app = webtest.TestApp(wsgiapp)
    yield app
    shutdown_app(app.app)


@pytest.yield_fixture(scope='function')
def app(global_app):
    yield global_app


@pytest.yield_fixture(scope='session')
def global_celery():
    init_worker(celery_app)
    yield celery_app
    shutdown_worker(celery_app)


@pytest.yield_fixture(scope='function')
def celery(global_celery):
    yield global_celery
