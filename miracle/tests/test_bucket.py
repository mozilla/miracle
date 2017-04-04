

def test_bucket(bucket, raven):
    assert bucket.ping(raven)

    bucket.put('foo', b'bar')
    obj = bucket.get('foo')
    assert obj['ContentType'] == 'application/json'
    body = obj['Body']
    assert body.read() == b'bar'
    body.close()


def test_bucket_delete(bucket):
    bucket.put('foo/bar', b'bar')
    bucket.put('foo/baz', b'baz')

    bucket.delete('foo/bar')
    assert bucket.get('foo/baz')['Body']
