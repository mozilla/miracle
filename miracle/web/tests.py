

def test_config(app):
    assert hasattr(app, 'app')
    assert hasattr(app.app, 'registry')
    assert hasattr(app.app.registry, 'crypto')
    assert hasattr(app.app.registry, 'kinesis')
    assert hasattr(app.app.registry, 'raven')
    assert hasattr(app.app.registry, 'stats')


def test_heartbeat(app, stats):
    res = app.get('/__heartbeat__', status=200)
    assert res.json == {'queue': {'up': True}}
    stats.check(counter=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:200']),
    ], timer=[
        ('request', 1, ['path:__heartbeat__', 'method:get', 'status:200']),
    ])


def test_heartbeat_queue_error(app, kinesis, raven, stats):
    kinesis._delete_frontend_stream()

    res = app.get('/__heartbeat__', status=503)
    assert res.status_code == 503
    assert res.json == {'queue': {'up': False}}
    raven.check(['ResourceNotFoundException'])


def test_index(app, stats):
    res = app.get('/', status=200)
    assert res.content_type == 'text/html'
    assert res.text.startswith('<!DOCTYPE html>')
    assert res.headers['Strict-Transport-Security'] == 'max-age=31536000'
    assert res.headers['Content-Security-Policy'] == "default-src 'self'"
    stats.check(counter=[
        ('request', 1, ['path:', 'method:get', 'status:200']),
    ], timer=[
        ('request', 1, ['path:', 'method:get', 'status:200']),
    ])


def test_lbheartbeat(app, stats):
    res = app.get('/__lbheartbeat__', status=200)
    assert res.json == {'status': 'OK'}
    stats.check(total=0)


def test_notfound(app, stats):
    res = app.get('/not-here', status=404)
    assert res.status_code == 404
    stats.check(total=0)


def test_robots(app, stats):
    res = app.get('/robots.txt', status=200)
    assert res.text.startswith('User-agent:')
    stats.check(total=0)


def test_settings():
    from miracle.web import settings
    assert isinstance(settings.max_requests_jitter, int)


def test_version(app, stats):
    res = app.get('/__version__')
    assert set(res.json.keys()) == {'build', 'commit', 'source', 'version'}
    stats.check(total=0)


def test_worker():
    from miracle.web import worker
    assert hasattr(worker, 'GeventWorker')
