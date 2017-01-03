import json

from jwcrypto.jwk import JWK

from miracle.api.views import (
    check_user,
)

CORS_HEADERS = {
    'Access-Control-Allow-Origin',
    'Access-Control-Max-Age',
    'Access-Control-Allow-Headers',
    'Access-Control-Allow-Methods',
}


def test_check_user():
    assert not check_user(None)
    assert not check_user('')
    assert not check_user(b'')
    assert not check_user(b'ab')
    assert not check_user(('a' * 40).encode('ascii'))
    assert not check_user(b'abcd?')
    assert not check_user(b'abcd\xfe')
    assert check_user('abc')
    assert check_user(b'abc')
    assert check_user('fae006df902d4809aaddb176b6bdf8dd')
    assert check_user(b'fae006df902d4809aaddb176b6bdf8dd')
    assert check_user('fae006df-902d-4809-aadd-b176b6bdf8dd')
    assert check_user(b'fae006df-902d-4809-aadd-b176b6bdf8dd')


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

    stats.check(timer=[
        ('task', 2, ['task:data.tasks.upload']),
    ])


def test_upload_fail(app, stats):
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'text/plain'},
             status=400)
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)
    app.post('/v1/upload', b'a' + b'0123456789' * 1024 * 1024,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)
    app.post('/v1/upload', b'no json',
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)
    app.post('/v1/upload', 'no\xfejson'.encode('latin-1'),
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)


def test_upload_jwe(app, stats):
    # Encrypt the data with a wrong key.
    jwk = JWK.generate(kty='RSA')
    data = app.app.registry.crypto.encrypt(
        b'{"key": "wrong"}', _public_jwk=jwk)
    app.post('/v1/upload', data,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=200)
    # Encrypt the data with a wrong algorithm.
    data = app.app.registry.crypto.encrypt(
        b'{"alg": "wrong"}',
        _protected='{"alg":"RSA-OAEP","enc":"A128CBC-HS256"}')
    app.post('/v1/upload', data,
             headers={'Content-Type': 'text/plain',
                      'X-User': b'abc'},
             status=400)


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
