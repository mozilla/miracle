

def test_delete(app):
    app.head('/v1/delete', status=200)
    res = app.post('/v1/delete',
                   '',
                   headers={'x-user': 'abc'},
                   status=200)
    assert res.json == {'status': 'success'}


def test_delete_unsupported(app):
    app.delete('/v1/delete', status=405)
    app.get('/v1/delete', status=405)
    app.options('/v1/delete', status=405)
    app.patch('/v1/delete', status=405)


def test_upload(app):
    app.head('/v1/upload', status=200)
    res = app.post_json('/v1/upload',
                        {'foo': 1},
                        headers={'x-user': 'abc'},
                        status=200)
    assert res.json == {'status': 'success'}


def test_upload_unsupported(app):
    app.delete('/v1/upload', status=405)
    app.get('/v1/upload', status=405)
    app.options('/v1/upload', status=405)
    app.patch('/v1/upload', status=405)
