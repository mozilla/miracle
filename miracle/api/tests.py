import json

from miracle.util import gzip_encode


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


def test_stats(app, stats):
    res = app.get('/v1/stats', status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {}
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


def test_upload_gzip(app, crypto):
    data = gzip_encode(crypto.encrypt(b'{"foo": 1}'))
    res = app.post('/v1/upload',
                   data,
                   headers={'Content-Encoding': 'gzip',
                            'Content-Type': 'text/plain',
                            'X-User': b'abc'},
                   status=200)
    assert res.json == {'status': 'success'}


def test_upload_gzip_fail(app):
    app.post('/v1/upload',
             b'invalid',
             headers={'Content-Encoding': 'gzip',
                      'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)


def test_head(app, stats):
    app.head('/v1/delete', status=200)
    app.head('/v1/upload', status=200)
    stats.check(timer=[
        ('request', ['path:v1.delete', 'method:head', 'status:200']),
        ('request', ['path:v1.upload', 'method:head', 'status:200']),
    ])


def test_options(app, stats):
    res = app.options('/v1/delete', status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()

    res = app.options('/v1/upload', status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()

    stats.check(timer=[
        ('request', ['path:v1.delete', 'method:options', 'status:200']),
        ('request', ['path:v1.upload', 'method:options', 'status:200']),
    ])


def test_unsupported(app, stats):
    app.delete('/v1/delete', status=405)
    app.get('/v1/delete', status=405)
    app.patch('/v1/delete', status=405)

    app.delete('/v1/upload', status=405)
    app.get('/v1/upload', status=405)
    app.patch('/v1/upload', status=405)

    assert not stats.msgs
