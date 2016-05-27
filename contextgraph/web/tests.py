import pytest
import webtest

from contextgraph.cache import create_cache
from contextgraph.web.app import (
    create_app,
    shutdown_app,
)


@pytest.yield_fixture(scope='function')
def broken_app():
    cache = create_cache('redis://127.0.0.1:9/15')

    wsgiapp = create_app(_cache=cache)
    app = webtest.TestApp(wsgiapp)
    yield app
    shutdown_app(app.app)

    cache.close()


def test_config(app):
    assert hasattr(app, 'app')
    assert hasattr(app.app, 'registry')


def test_heartbeat(app):
    res = app.get('/__heartbeat__')
    assert res.status_code == 200
    assert res.json == {'redis': {'up': True}}


def test_heartbeat_error(broken_app):
    res = broken_app.get('/__heartbeat__', status=503)
    assert res.status_code == 503
    assert res.json == {'redis': {'up': False}}


def test_index(app):
    res = app.get('/')
    assert res.status_code == 200
    assert res.text.startswith('It works')


def test_lbheartbeat(app):
    res = app.get('/__lbheartbeat__')
    assert res.status_code == 200
    assert res.json == {'status': 'OK'}


def test_robots(app):
    res = app.get('/robots.txt')
    assert res.status_code == 200
    assert res.text.startswith('User-agent:')


def test_settings():
    from contextgraph.web import settings
    assert type(settings.max_requests_jitter) == int


def test_version(app):
    res = app.get('/__version__')
    keys = set(res.json.keys())
    assert keys == {'build', 'commit', 'source', 'version'}


def test_worker():
    from contextgraph.web import worker
    assert hasattr(worker, 'GeventWorker')
