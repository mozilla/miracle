CORS_HEADERS = {
    'Access-Control-Allow-Origin',
    'Access-Control-Max-Age',
    'Access-Control-Allow-Headers',
    'Access-Control-Allow-Methods',
}


def test_delete(app):
    res = app.post('/v1/delete',
                   '',
                   headers={'X-User': 'abc'},
                   status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}


def test_delete_fail(app, stats):
    app.post('/v1/delete', 'foo', status=400)
    app.post('/v1/delete', 'foo', headers={'X-User': 'abc'}, status=400)
    stats.check(timer=[
        ('request', 2, ['path:v1.delete', 'method:post', 'status:400']),
    ])


def test_upload(app):
    res = app.post_json('/v1/upload',
                        {'foo': 1},
                        headers={'X-User': 'abc'},
                        status=200)
    assert CORS_HEADERS - set(res.headers.keys()) == set()
    assert res.json == {'status': 'success'}


def test_upload_fail(app, stats):
    app.post('/v1/upload', '', status=400)
    app.post('/v1/upload', '', headers={'X-User': 'abc'}, status=400)
    stats.check(timer=[
        ('request', 2, ['path:v1.upload', 'method:post', 'status:400']),
    ])


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
