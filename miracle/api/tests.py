import json


CORS_HEADERS = {
    'Access-Control-Allow-Origin',
    'Access-Control-Max-Age',
    'Access-Control-Allow-Headers',
    'Access-Control-Allow-Methods',
}


def test_delete(app, stats):
    res = app.post('/v1/delete',
                   b'',
                   headers={'X-User': b'abc'},
                   status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}
    assert 'Strict-Transport-Security' in res.headers
    stats.check(timer=[
        ('task', 1, ['task:data.tasks.delete']),
    ])


def test_delete_fail(app, stats):
    app.post('/v1/delete', b'foo', status=400)
    app.post('/v1/delete', b'foo', headers={'X-User': b'abc'}, status=400)
    stats.check(timer=[
        ('request', 2, ['path:v1.delete', 'method:post', 'status:400']),
    ])


def test_jwk(app, stats):
    res = app.get('/v1/jwk', status=200)
    assert set(res.json.keys()) == {'n', 'e', 'kty'}
    assert res.json['kty'] == 'RSA'
    assert 'Strict-Transport-Security' in res.headers
    stats.check(timer=[
        ('request', 1, ['path:v1.jwk', 'method:get', 'status:200']),
    ])


def test_stats(app, stats):
    res = app.get('/v1/stats', status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {}
    assert 'Strict-Transport-Security' in res.headers
    stats.check(timer=[
        ('request', 1, ['path:v1.stats', 'method:get', 'status:200']),
    ])


def test_upload(app, crypto, stats):
    data = crypto.encrypt(json.dumps({'foo': 1}))
    res = app.post('/v1/upload',
                   data,
                   headers={'Content-Type': 'text/plain',
                            'X-User': b'abc'},
                   status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}
    assert 'Strict-Transport-Security' in res.headers

    data = crypto.encrypt(b'encrypted no json')
    app.post('/v1/upload', data,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=200)

    data = b'no json'
    app.post('/v1/upload', data,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=200)

    stats.check(timer=[
        ('task', 3, ['task:data.tasks.upload']),
    ])


def test_upload_fail(app, stats):
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'text/plain'},
             status=400)
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)
    too_large = b'a' + b'0123456789' * 1024 * 1024
    app.post('/v1/upload', too_large,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)
    stats.check(timer=[
        ('request', 3, ['path:v1.upload', 'method:post', 'status:400']),
    ])


def test_head(app, stats):
    urls = [
        '/v1/delete',
        '/v1/jwk',
        '/v1/stats',
        '/v1/upload',
    ]
    for url in urls:
        app.head(url, status=200)


def test_options(app, stats):
    urls = {
        # url: primary supported method
        '/v1/delete': 'POST',
        '/v1/jwk': 'GET',
        '/v1/stats': 'GET',
        '/v1/upload': 'POST',
    }
    for url, method in urls.items():
        res = app.options(url, status=200)
        assert CORS_HEADERS - set(res.headers.keys()) == set()
        assert method in res.headers['Access-Control-Allow-Methods']


def test_unsupported(app, stats):
    urls = {
        # url: unsupported method
        '/v1/delete': 'get',
        '/v1/jwk': 'post',
        '/v1/stats': 'post',
        '/v1/upload': 'get',
    }
    for url, method in urls.items():
        app.delete(url, status=405)
        app.patch(url, status=405)
        if method == 'post':
            getattr(app, method)(url, b'', status=405)
        else:
            getattr(app, method)(url, status=405)

    assert not stats.msgs
