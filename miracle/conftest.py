import gc
import warnings

from alembic import command
import pytest
from sqlalchemy import (
    inspect,
    text,
)
import webtest

from miracle.bucket import create_bucket
from miracle.cache import create_cache
from miracle.config import ALEMBIC_CFG
from miracle.db import create_db
from miracle.log import (
    create_raven,
    create_stats,
)
from miracle.models import Model
from miracle.web.app import (
    create_app,
    shutdown_app,
)
from miracle.worker.app import (
    celery_app,
    init_worker,
    shutdown_worker,
)


def setup_db(engine):
    with engine.connect() as conn:
        # Create all tables from model definition.
        trans = conn.begin()
        Model.metadata.create_all(engine)
        trans.commit()
    # Finally stamp the database with the latest alembic version.
    command.stamp(ALEMBIC_CFG, 'head')


def teardown_db(engine):
    inspector = inspect(engine)
    with engine.connect() as conn:
        # Drop all tables currently in the database.
        trans = conn.begin()
        names = inspector.get_table_names()
        if names:  # pragma: no cover
            conn.execute(text('DROP TABLE %s' % ', '.join(names)))
        trans.commit()


@pytest.yield_fixture(scope='session', autouse=True)
def package():
    # Apply gevent monkey patches as early as possible during tests.
    from gevent.monkey import patch_all
    patch_all()
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()

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
def global_bucket():
    bucket = create_bucket()
    yield bucket


@pytest.yield_fixture(scope='function')
def bucket(global_bucket):
    yield global_bucket
    global_bucket.clear()


@pytest.yield_fixture(scope='session')
def global_cache():
    cache = create_cache()
    yield cache
    cache.close()


@pytest.yield_fixture(scope='function')
def cache(global_cache):
    yield global_cache
    global_cache.flushdb()


@pytest.yield_fixture(scope='session')
def global_db():
    db = create_db()
    teardown_db(db.engine)
    setup_db(db.engine)
    yield db
    db.close()


@pytest.yield_fixture(scope='session')
def db(global_db):
    conn = global_db.engine.connect()
    trans = conn.begin()
    global_db.session_factory.configure(bind=conn)
    with global_db.session(commit=False) as session:
        yield global_db
        session.rollback()
    global_db.session_factory.configure(bind=None)
    trans.rollback()
    trans.close()
    conn.close()


@pytest.yield_fixture(scope='session')
def global_raven():
    raven = create_raven()
    yield raven


@pytest.yield_fixture(scope='function')
def raven(global_raven):
    yield global_raven
    messages = [msg['message'] for msg in global_raven.msgs]
    global_raven.clear()
    assert not messages


@pytest.yield_fixture(scope='session')
def global_stats():
    stats = create_stats()
    yield stats
    stats.close()


@pytest.yield_fixture(scope='function')
def stats(global_stats):
    yield global_stats
    global_stats.clear()


@pytest.yield_fixture(scope='session')
def global_celery(global_bucket, global_cache, global_db,
                  global_raven, global_stats):
    init_worker(
        celery_app,
        _bucket=global_bucket,
        _cache=global_cache,
        _db=global_db,
        _raven=global_raven,
        _stats=global_stats)
    yield celery_app
    shutdown_worker(celery_app)


@pytest.yield_fixture(scope='function')
def celery(global_celery, bucket, cache, db, raven, stats):
    yield global_celery


@pytest.yield_fixture(scope='session')
def global_app(global_cache, global_celery, global_db,
               global_raven, global_stats):
    wsgiapp = create_app(
        _cache=global_cache,
        _db=global_db,
        _raven=global_raven,
        _stats=global_stats)
    app = webtest.TestApp(wsgiapp)
    yield app
    shutdown_app(app.app)


@pytest.yield_fixture(scope='function')
def app(global_app, cache, celery, db, raven, stats):
    yield global_app
