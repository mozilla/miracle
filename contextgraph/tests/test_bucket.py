

def test_bucket(bucket):
    bucket.put('foo', b'bar')
    obj = bucket.get('foo')
    assert obj['ContentEncoding'] is None
    assert obj['ContentType'] == 'application/json'
    body = obj['Body']
    assert body.read() == b'bar'
    body.close()


def test_bucket_delete(bucket):
    bucket.put('foo', b'')
    bucket.put('foo/bar', b'')
    bucket.put('foo/baz', b'')

    bucket.delete('foo/bar')
    assert bucket.get('foo/baz')['Body']

    bucket.delete('foo')
    assert bucket.objects == {}
