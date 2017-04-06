import gzip
import json

from miracle.data import tasks
from miracle.data import upload


class DummyTask(object):

    def __init__(self, bucket=None, crypto=None, raven=None, stats=None):
        self.bucket = bucket
        self.crypto = crypto
        self.raven = raven
        self.stats = stats


def test_validate_user():
    assert not upload.validate_user(None)
    assert not upload.validate_user(b'')
    assert not upload.validate_user(b'abcdefgh')
    assert not upload.validate_user('')
    assert not upload.validate_user('ab')
    assert not upload.validate_user('a' * 40)
    assert not upload.validate_user('abcd?')
    assert not upload.validate_user('abcd\xfe')
    assert upload.validate_user('foo')
    assert upload.validate_user('fae006df902d4809aaddb176b6bdf8dd')
    assert upload.validate_user('fae006df-902d-4809-aadd-b176b6bdf8dd')


def test_validate():
    invalid_inputs = [
        {'other_key': []},
        {'user': 123},
        {'user': 123, 'other': []},
        {'user': b'ab', 'other': []},
    ]
    for invalid in invalid_inputs:
        assert not upload.validate(invalid)

    valid_inputs = [
        {'user': 'foo'},
        {'user': 'foo', 'other': [{}]},
        {'user': 'foo', 'other': [], 'another': 'abc'},
    ]
    for valid in valid_inputs:
        assert upload.validate(valid) == valid


def test_upload(bucket, raven, stats):
    payload = {'user': 'foo', 'other': ['spam', 'eggs']}

    user = payload['user']
    task = DummyTask(bucket=bucket, raven=raven, stats=stats)
    assert upload.upload(task, payload)

    objs = list(bucket.filter(Prefix='v2/sessions/%s/' % user))
    assert len(objs) == 1
    assert objs[0].key.endswith('.json.gz')

    obj = bucket.get(objs[0].key)
    assert obj['ContentEncoding'] == 'gzip'
    assert obj['ContentType'] == 'application/json'
    body = obj['Body'].read()
    obj['Body'].close()

    body = json.loads(gzip.decompress(body).decode('utf-8'))
    assert body == payload

    # Upload a second time
    assert upload.upload(task, payload)

    objs = list(bucket.filter(Prefix='v2/sessions/%s/' % user))
    assert len(objs) == 2


def test_task(celery, crypto, stats):
    payload = {'user': 'foo', 'other': ['spam', 'eggs']}

    assert tasks.upload.delay(
        crypto.encrypt(json.dumps(payload))).get()


def test_task_fail(celery, crypto, stats):
    assert not tasks.upload.delay(
        crypto.encrypt(b'no json')).get()

    assert not tasks.upload.delay(
        crypto.encrypt(b'{"user": 123}')).get()

    assert not tasks.upload.delay(
        crypto.encrypt(b'{"other": [{}]}')).get()

    stats.check(counter=[
        ('data.upload.error', 1, ['reason:json']),
        ('data.upload.error', 2, ['reason:validation']),
    ])
