

def test_bucket(bucket, raven):
    assert bucket.ping(raven)

    bucket.put('foo', b'bar', ContentType='application/json')
    obj = bucket.get('foo')
    assert obj['ContentType'] == 'application/json'
    body = obj['Body']
    assert body.read() == b'bar'
    body.close()


def test_bucket_delete(bucket):
    bucket.put('foo/bar', b'bar')
    bucket.put('foo/baz', b'baz')

    objs = list(bucket.filter(Prefix='foo/'))
    assert len(objs) == 2

    bucket.delete('foo/bar')
    body = bucket.get('foo/baz')['Body']
    assert body.read()
    body.close()

    objs = list(bucket.filter(Prefix='foo/'))
    assert len(objs) == 1
