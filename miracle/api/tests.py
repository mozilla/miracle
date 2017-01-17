import json

from jwcrypto.jwk import JWK

CORS_HEADERS = {
    'Access-Control-Allow-Origin',
    'Access-Control-Max-Age',
    'Access-Control-Allow-Headers',
    'Access-Control-Allow-Methods',
}


def test_jwk(app, stats):
    res = app.get('/v2/jwk', status=200)
    assert set(res.json.keys()) == {'n', 'e', 'kty'}
    assert res.json['kty'] == 'RSA'
    assert 'Strict-Transport-Security' in res.headers
    stats.check(timer=[
        ('request', 1, ['path:v2.jwk', 'method:get', 'status:200']),
    ])


def test_upload(app, crypto, stats):
    data = crypto.encrypt(json.dumps({'foo': 1}))
    res = app.post('/v2/upload', data,
                   headers={'Content-Type': 'text/plain'},
                   status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}
    assert 'Strict-Transport-Security' in res.headers

    data = crypto.encrypt(b'encrypted no json')
    app.post('/v2/upload', data,
             headers={'Content-Type': 'text/plain'},
             status=200)

    stats.check(timer=[
        ('task', 2, ['task:data.tasks.upload']),
    ])


def test_upload_fail(app, stats):
    app.post('/v2/upload', b'',
             headers={'Content-Type': 'text/plain'},
             status=400)
    app.post('/v2/upload', b'a' + b'0123456789' * 1024 * 1024,
             headers={'Content-Type': 'text/plain'},
             status=400)
    app.post('/v2/upload', b'no json',
             headers={'Content-Type': 'text/plain'},
             status=400)
    app.post('/v2/upload', 'no\xfejson'.encode('latin-1'),
             headers={'Content-Type': 'text/plain'},
             status=400)


def test_upload_jwe(app, stats):
    # Encrypt the data with a wrong key.
    jwk = JWK.generate(kty='RSA')
    data = app.app.registry.crypto.encrypt(
        b'{"key": "wrong"}', _public_jwk=jwk)
    app.post('/v2/upload', data,
             headers={'Content-Type': 'text/plain'},
             status=200)
    # Encrypt the data with a wrong algorithm.
    data = app.app.registry.crypto.encrypt(
        b'{"alg": "wrong"}',
        _protected='{"alg":"RSA-OAEP","enc":"A128CBC-HS256"}')
    app.post('/v2/upload', data,
             headers={'Content-Type': 'text/plain'},
             status=400)


def test_head(app, stats):
    urls = [
        '/v2/jwk',
        '/v2/upload',
    ]
    for url in urls:
        app.head(url, status=200)


def test_options(app, stats):
    urls = {
        # url: primary supported method
        '/v2/jwk': 'GET',
        '/v2/upload': 'POST',
    }
    for url, method in urls.items():
        res = app.options(url, status=200)
        assert CORS_HEADERS - set(res.headers.keys()) == set()
        assert method in res.headers['Access-Control-Allow-Methods']


def test_unsupported(app, stats):
    urls = {
        # url: unsupported method
        '/v2/jwk': 'post',
        '/v2/upload': 'get',
    }
    for url, method in urls.items():
        app.delete(url, status=405)
        app.patch(url, status=405)
        if method == 'post':
            getattr(app, method)(url, b'', status=405)
        else:
            getattr(app, method)(url, status=405)

    assert not stats.msgs
