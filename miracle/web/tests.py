import pytest
import webtest

from miracle.cache import create_cache
from miracle.web.app import (
    create_app,
    shutdown_app,
)


@pytest.yield_fixture(scope='function')
def broken_app(raven, stats):
    cache = create_cache('redis://127.0.0.1:9/15')

    wsgiapp = create_app(_cache=cache, _raven=raven, _stats=stats)
    raven.check(['ConnectionError'])

    app = webtest.TestApp(wsgiapp)
    yield app
    shutdown_app(app.app)

    cache.close()


def test_config(app):
    assert hasattr(app, 'app')
    assert hasattr(app.app, 'registry')
    assert hasattr(app.app.registry, 'cache')
    assert hasattr(app.app.registry, 'raven')
    assert hasattr(app.app.registry, 'stats')


def test_heartbeat(app, stats):
    res = app.get('/__heartbeat__')
    assert res.status_code == 200
    assert res.json == {'redis': {'up': True}}
    stats.check(counter=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:200']),
    ], timer=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:200']),
    ])


def test_heartbeat_error(broken_app, raven, stats):
    res = broken_app.get('/__heartbeat__', status=503)
    assert res.status_code == 503
    assert res.json == {'redis': {'up': False}}
    stats.check(counter=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:503']),
    ], timer=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:503']),
    ])
    raven.check(['ConnectionError'])


def test_index(app, stats):
    res = app.get('/')
    assert res.status_code == 200
    assert res.text.startswith('It works')
    stats.check(counter=[
        ('request', 1, ['path:', 'method:get', 'status:200']),
    ], timer=[
        ('request', 1, ['path:', 'method:get', 'status:200']),
    ])


def test_lbheartbeat(app, stats):
    res = app.get('/__lbheartbeat__')
    assert res.status_code == 200
    assert res.json == {'status': 'OK'}
    stats.check(total=0)


def test_notfound(app, stats):
    res = app.get('/not-here', status=404)
    assert res.status_code == 404
    stats.check(total=0)


def test_robots(app, stats):
    res = app.get('/robots.txt')
    assert res.status_code == 200
    assert res.text.startswith('User-agent:')
    stats.check(total=0)


def test_settings():
    from miracle.web import settings
    assert type(settings.max_requests_jitter) == int


def test_version(app, stats):
    res = app.get('/__version__')
    keys = set(res.json.keys())
    assert keys == {'build', 'commit', 'source', 'version'}
    stats.check(total=0)


def test_worker():
    from miracle.web import worker
    assert hasattr(worker, 'GeventWorker')
