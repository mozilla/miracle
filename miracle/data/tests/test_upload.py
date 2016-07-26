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


class DummyTask(object):

    def __init__(self, cache=None):
        self.cache = cache


def test_validate():
    url = 'https://example.com/path'
    time = 1469400000

    invalid_inputs = [
        {'other_key': []},
        {'sessions': {}},
        {'sessions': [[]]},
        {'sessions': [{'url': ''}]},
        {'sessions': [{'url': 1}]},
        {'sessions': [{'url': url, 'start_time': None}]},
        {'sessions': [{'url': 'https://example.com/' + 'abc/' * 512,
                       'start_time': time}]},
        {'sessions': [{'url': 'https://admin:admin@example.com/',
                       'start_time': time}]},
    ]
    for invalid in invalid_inputs:
        assert not upload.validate(invalid)

    valid_inputs = [
        {'sessions': [{'url': url, 'start_time': time, 'duration': None}]},
        {'sessions': [{'url': url, 'start_time': time, 'duration': 2400}]},
    ]
    for valid in valid_inputs:
        assert upload.validate(valid) == valid

    corrected_inputs = [(
        {'sessions': [{'url': url, 'start_time': time, 'duration': -100}]},
        {'sessions': [{'url': url, 'start_time': time, 'duration': None}]}
    )]
    for input_, expected in corrected_inputs:
        assert upload.validate(input_) == expected


def test_upload_data(cache):
    task = DummyTask(cache=cache)
    assert upload.upload_data(task, 'foo', _PAYLOAD)
    assert b'user_foo' in cache.keys()
    assert cache.get(b'user_foo') == upload.json_encode(_PAYLOAD)
    assert cache.ttl(b'user_foo') <= 3600


def test_upload_main(cache):
    def _upload(task, user, data):
        return (user, data)

    task = DummyTask(cache=cache)
    result = upload.main(
        task, 'foo', json.dumps(_PAYLOAD), _upload_data=_upload)
    assert result == ('foo', _PAYLOAD)


def test_task(celery):
    assert tasks.upload.delay(
        'foo', json.dumps(_PAYLOAD).encode('utf-8'), _upload_data=False).get()


def test_task_fail(celery):
    assert not tasks.upload.delay(
        'foo', b'no json', _upload_data=False).get()
