from datetime import date
import functools
import gzip
import json

from miracle.stream.frontend_s3 import (
    main,
    validate,
    validate_user,
)
from miracle.stream.tests.conftest import make_record


def _payload(crypto, data):
    data = json.dumps(data).encode('utf-8')
    return crypto.encrypt(data).encode('ascii')


def test_validate_user():
    assert not validate_user(None)
    assert not validate_user(b'')
    assert not validate_user(b'abcdefgh')
    assert not validate_user('')
    assert not validate_user('ab')
    assert not validate_user('a' * 40)
    assert not validate_user('abcd?')
    assert not validate_user('abcd\xfe')
    assert validate_user('foo')
    assert validate_user('fae006df902d4809aaddb176b6bdf8dd')
    assert validate_user('fae006df-902d-4809-aadd-b176b6bdf8dd')


def test_validate():
    invalid_inputs = [
        {'other_key': []},
        {'user': 123},
        {'user': 123, 'other': []},
        {'user': b'ab', 'other': []},
    ]
    for invalid in invalid_inputs:
        assert not validate(invalid)

    valid_inputs = [
        {'user': 'foo'},
        {'user': 'foo', 'other': [{}]},
        {'user': 'foo', 'other': [], 'another': 'abc'},
    ]
    for valid in valid_inputs:
        assert validate(valid) == valid


def test_main(bucket, crypto, processor):
    _p = functools.partial(_payload, crypto)
    today = date.today()
    user = 'foo'
    prefix = 'v2/sessions/%s/%s/%s/' % (today.year, today.month, user)

    records = [
        make_record('2', _p({'user': user, 'extra': 1})),
    ]
    assert main(processor, records) == ('2', 0)

    objs = list(bucket.filter(Prefix=prefix))
    assert len(objs) == 1
    assert objs[0].key.endswith('.json.gz')

    obj = bucket.get(objs[0].key)
    assert obj['ContentEncoding'] == 'gzip'
    assert obj['ContentType'] == 'application/json'
    body = obj['Body'].read()
    obj['Body'].close()

    body = json.loads(gzip.decompress(body).decode('utf-8'))
    assert body == {'user': user, 'extra': 1}

    # Upload a second time
    records = [
        make_record('3', _p({'user': user, 'extra': 2})),
    ]
    assert main(processor, records) == ('3', 0)

    objs = list(bucket.filter(Prefix=prefix))
    assert len(objs) == 2


def test_main_fail(crypto, processor, stats):
    payload = b'not encrypted'
    records = [make_record('1', payload)]
    assert main(processor, records) != ('1', 0)

    payload = crypto.encrypt(b'no json').encode('ascii')
    records = [make_record('2', payload)]
    assert main(processor, records) != ('2', 0)

    payload = crypto.encrypt(json.dumps({'no': 'user'})).encode('ascii')
    records = [make_record('3', payload)]
    assert main(processor, records) != ('3', 0)

    stats.check(counter=[
        ('data.upload.error', 1, ['reason:encryption']),
        ('data.upload.error', 1, ['reason:json']),
        ('data.upload.error', 1, ['reason:validation']),
    ])
