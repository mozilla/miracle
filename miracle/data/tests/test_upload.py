import json

from miracle.data import tasks
from miracle.data import upload

_PAYLOAD = {'sessions': [
    {
        "duration": 2400,
        "start_time": 1468600000,
        "url": "http://www.example.com/",
    },
    {
        "duration": 1300,
        "start_time": 1468800000,
        "url": "https://www.foo.com/",
    },
    {
        "duration": 5700,
        "start_time": 1469200000,
        "url": "https://www.example.com/login",
    },
    {
        "duration": 4600,
        "start_time": 1469400000,
        "url": "http://www.example.com/search/?query=question",
    },

]}


def test_upload(cache, celery, stats):
    assert tasks.upload.delay(
        'foo', json.dumps(_PAYLOAD).encode('utf-8')).get()

    assert b'user_foo' in cache.keys()
    assert cache.get(b'user_foo') == upload.json_encode(_PAYLOAD)
    assert cache.ttl(b'user_foo') <= 3600


def test_upload_fail(cache, celery, stats):
    assert not tasks.upload.delay('foo', b'no json').get()


def test_validate():
    url = 'https://example.com/path'

    invalid_inputs = [
        {'other_key': []},
        {'sessions': {}},
        {'sessions': [[]]},
        {'sessions': [{'url': ''}]},
        {'sessions': [{'url': 1}]},
    ]
    for invalid in invalid_inputs:
        assert not upload.validate(invalid)

    valid_inputs = [
        {'sessions': [{'url': url, 'start_time': None, 'duration': 0}]},
        {'sessions': [{'url': url, 'start_time': 0, 'duration': 2400}]},
        {'sessions': [{'url': url, 'start_time': 1469300000,
                       'duration': 3700}]},
    ]
    for valid in valid_inputs:
        assert upload.validate(valid) == valid
