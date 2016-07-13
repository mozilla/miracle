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


def test_upload(app, stats):
    res = app.post_json('/v1/upload',
                        {'foo': 1},
                        headers={'Content-Type': 'application/json',
                                 'X-User': b'abc'},
                        status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}
    stats.check(timer=[
        ('task', 1, ['task:data.tasks.upload']),
    ])


def test_upload_fail(app, stats):
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'application/json'},
             status=400)
    app.post('/v1/upload', b'',
             headers={'Content-Type': 'application/json',
                      'X-User': b'abc'},
             status=400)
    app.post('/v1/upload', b'invalid',
             headers={'Content-Type': 'application/json',
                      'X-User': b'abc'},
             status=400)
    stats.check(timer=[
        ('request', 3, ['path:v1.upload', 'method:post', 'status:400']),
    ])


def test_upload_gzip(app):
    res = app.post('/v1/upload',
                   gzip_encode('{"foo": 1}'),
                   headers={'Content-Encoding': 'gzip',
                            'Content-Type': 'application/json',
                            'X-User': b'abc'},
                   status=200)
    assert res.json == {'status': 'success'}


def test_upload_gzip_fail(app):
    app.post('/v1/upload',
             b'invalid',
             headers={'Content-Encoding': 'gzip',
                      'Content-Type': 'application/json',
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
