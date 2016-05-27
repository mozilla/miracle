

def test_config(app):
    assert hasattr(app, 'app')
    assert hasattr(app.app, 'registry')


def test_heartbeat(app):
    res = app.get('/__heartbeat__')
    assert res.status_code == 200
    assert res.json == {}


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
