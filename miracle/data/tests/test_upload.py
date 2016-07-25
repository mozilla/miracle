import json

from miracle.data import tasks
from miracle.data import upload

_PAYLOAD = {'history': [
    {
        "lastAccessTime": 1468600000,
        "uri": "http://www.example.com/",
        "title": "Example",
    },
    {
        "lastAccessTime": 1468900000,
        "uri": "https://www.foo.com/",
        "title": "Fö\\\\u00f6",
    },
    {
        "lastAccessTime": 1469300000,
        "uri": "https://www.example.com/login",
        "title": "Example",
    },
    {
        "lastAccessTime": 1469400000,
        "uri": "http://www.example.com/search/?query=question",
        "title": "Example",
    },

]}


def test_upload(cache, celery, stats):
    assert tasks.upload.delay(
        'foo', json.dumps(_PAYLOAD).encode('utf-8')).get()

    assert b'user_foo' in cache.keys()
    compact = json.dumps(_PAYLOAD, separators=(',', ':')).encode('utf-8')
    assert cache.get(b'user_foo') == compact
    assert cache.ttl(b'user_foo') <= 3600


def test_upload_fail(cache, celery, stats):
    assert not tasks.upload.delay('foo', b'no json').get()


def test_validate():
    uri = 'https://example.com'

    invalid_inputs = [
        {'other_key': []},
        {'history': {}},
        {'history': [[]]},
        {'history': [{'uri': ''}]},
        {'history': [{'uri': 1}]},
    ]
    for invalid in invalid_inputs:
        assert not upload.validate(invalid)

    valid_inputs = [
        {'history': [{'uri': uri, 'lastAccessTime': None, 'title': ''}]},
        {'history': [{'uri': uri, 'lastAccessTime': 0, 'title': 'abc'}]},
        {'history': [{'uri': uri, 'lastAccessTime': 1469300000,
                      'title': 'abc'}]},
    ]
    for valid in valid_inputs:
        assert upload.validate(valid) == valid
