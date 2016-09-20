from copy import deepcopy
from datetime import datetime
import json
from unittest import mock

from sqlalchemy.dialects.postgresql import insert

from miracle.data import tasks
from miracle.data import upload
from miracle.models import (
    URL,
    User,
    Session,
)

TEST_TIME = datetime.utcfromtimestamp(1469400000)
_PAYLOAD = {'sessions': [
    {
        'duration': 2400,
        'start_time': 1468600000,
        'url': 'http://www.example.com/',
        'tab_id': '-31-1',
    },
    {
        'duration': 1300,
        'start_time': 1468800000,
        'url': 'https://www.foo.com/',
        'tab_id': '-31-1',
    },
    {
        'duration': 5700,
        'start_time': 1469200000,
        'url': 'https://www.example.com/login',
        'tab_id': '-31-1',
    },
    {
        'duration': 4600,
        'start_time': 1469400000,
        'url': 'http://www.example.com/search/?query=question',
        'tab_id': '-30-2',
    },
    {
        'duration': 6200,
        'start_time': 1469500000,
        'url': 'https://www.foo.com/',
        'tab_id': '-30-2',
    },
]}
_INVALID_SESSIONS = [
    {
        'duration': 800,
        'start_time': 1469700000,
        'url': 'https://foo:admin@www.foo.com/',
        'tab_id': '-10-1',
    }, {
        'duration': 1000,
        'start_time': 1469800000,
        'url': 'https://foo:admin@www.foo.com/',
        'tab_id': '-10-1',
    }
]
_PAYLOAD_DURATIONS = {sess['duration'] for sess in _PAYLOAD['sessions']}
_PAYLOAD_STARTS = {datetime.utcfromtimestamp(sess['start_time'])
                   for sess in _PAYLOAD['sessions']}
_PAYLOAD_URLS = {sess['url'] for sess in _PAYLOAD['sessions']}
_PAYLOAD_TAB_IDS = {sess['tab_id'] for sess in _PAYLOAD['sessions']}
_COMBINED_PAYLOAD = deepcopy(_PAYLOAD)
_COMBINED_PAYLOAD['sessions'].extend(_INVALID_SESSIONS)


class DummyTask(object):

    def __init__(self, bloom_domain=None, crypto=None, db=None,
                 raven=None, stats=None):
        self.bloom_domain = bloom_domain
        self.crypto = crypto
        self.db = db
        self.raven = raven
        self.stats = stats


def test_validate(bloom_domain):
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
        {'sessions': [{'url': 'http://127.0.0.1/home', 'start_time': time}]},
        {'sessions': [{'url': 'about:config', 'start_time': time}]},
        {'sessions': [{'url': 'file:///etc/hosts', 'start_time': time}]},
        {'sessions': [{'url': 'https://admin:admin@example.com/',
                       'start_time': time}]},
        {'sessions': [{'url': 'http://localhost:80/', 'start_time': time}]},
    ]
    for invalid in invalid_inputs:
        assert not upload.validate(invalid, bloom_domain)[0]['sessions']

    valid_inputs = [
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': None, 'tab_id': None}]},
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': 2400, 'tab_id': None}]},
        {'sessions': [{'url': 'http://13.0.0.1/home', 'start_time': time,
                       'duration': None, 'tab_id': None}]},
        {'sessions': [{'url': 'http://13.0.0.1/home', 'start_time': time,
                       'duration': None, 'tab_id': '-20-2'}]},
    ]
    for valid in valid_inputs:
        assert upload.validate(valid, bloom_domain)[0] == valid

    corrected_inputs = [(
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': -100, 'tab_id': None}]},
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': 0, 'tab_id': None}]}
    ), (
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': upload.MAX_DURATION + 1, 'tab_id': None}]},
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': upload.MAX_DURATION, 'tab_id': None}]}
    ), (
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': None, 'tab_id': 'a'}]},
        {'sessions': [{'url': url, 'start_time': time,
                       'duration': None, 'tab_id': ''}]}
    )]
    for input_, expected in corrected_inputs:
        assert upload.validate(input_, bloom_domain)[0] == expected


def test_upload_data_new_user(bloom_domain, db, raven, stats):
    with db.session(commit=False) as session:
        url = URL(**URL.from_url('http://www.example.com/'))
        session.add(url)
        session.commit()

        task = DummyTask(bloom_domain=bloom_domain, db=db,
                         raven=raven, stats=stats)
        assert upload.upload_data(task, 'foo', _PAYLOAD)

        assert session.query(URL).count() == 4
        users = session.query(User).all()
        assert len(users) == 1
        assert users[0].token == 'foo'
        assert users[0].created.date() == datetime.utcnow().date()

        sessions = session.query(Session).all()
        assert len(sessions) == 5
        assert {sess.duration for sess in sessions} == _PAYLOAD_DURATIONS
        assert {sess.start_time for sess in sessions} == _PAYLOAD_STARTS
        assert {sess.tab_id for sess in sessions} == _PAYLOAD_TAB_IDS
        assert {sess.url.url for sess in sessions} == _PAYLOAD_URLS

    stats.check(counter=[
        ('data.session.new', 1, 5),
        ('data.url.new', 1, 3),
        ('data.user.new', 1, 1)
    ])


def test_upload_data_existing_user(bloom_domain, db, raven, stats):
    with db.session(commit=False) as session:
        user = User(token='foo', created=TEST_TIME)
        session.add(user)
        session.commit()

        task = DummyTask(bloom_domain=bloom_domain, db=db,
                         raven=raven, stats=stats)
        assert upload.upload_data(task, 'foo', _PAYLOAD)

        assert session.query(URL).count() == 4
        users = session.query(User).all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].token == 'foo'
        assert users[0].created == TEST_TIME

        sessions = session.query(Session).all()
        assert len(sessions) == 5
        assert {sess.duration for sess in sessions} == _PAYLOAD_DURATIONS
        assert {sess.start_time for sess in sessions} == _PAYLOAD_STARTS
        assert {sess.tab_id for sess in sessions} == _PAYLOAD_TAB_IDS
        assert {sess.url.url for sess in sessions} == _PAYLOAD_URLS

    stats.check(counter=[
        ('data.session.new', 1, 5),
        ('data.url.new', 1, 4),
        ('data.user.new', 0),
    ])


def test_upload_data_duplicated_sessions(bloom_domain, db, raven, stats):
    with db.session(commit=False) as session:
        task = DummyTask(bloom_domain=bloom_domain, db=db,
                         raven=raven, stats=stats)
        assert upload.upload_data(task, 'foo', _PAYLOAD)
        assert upload.upload_data(task, 'foo', _PAYLOAD)
        assert session.query(Session).count() == 10

    stats.check(counter=[
        ('data.session.new', 2, 5),
        ('data.url.new', 1, 4),
        ('data.user.new', 1, 1),
    ])


def test_upload_data_conflict(bloom_domain, cleanup_db, db, raven, stats):
    # Use as secondary transaction to insert a conflicting user id,
    # and keep it open while _upload_data runs the first time.
    # Rollback the secondary transaction before _upload_data runs
    # for the second time, to let it succeed.
    with cleanup_db.engine.connect() as conn:
        with conn.begin() as trans:
            conn.execute(insert(User), [{'token': 'foo'}])

            orig_upload_data = upload._upload_data
            num = 0

            def mock_upload_data(task, user_token, data, _lock_timeout=100):
                nonlocal num
                if num == 1:
                    trans.rollback()
                num += 1
                return orig_upload_data(task, user_token, data,
                                        _lock_timeout=_lock_timeout)

            with mock.patch.object(upload, '_upload_data', mock_upload_data):
                with db.session(commit=False) as session:
                    task = DummyTask(bloom_domain=bloom_domain, db=db,
                                     raven=raven, stats=stats)
                    assert upload.upload_data(
                        task, 'foo', _PAYLOAD,
                        _lock_timeout=100, _retry_wait=0.01)
                    assert num == 2
                    assert session.query(User).count() == 1
                    assert session.query(Session).count() == 5


def test_upload_data_conflict_error(bloom_domain, cleanup_db, db,
                                    raven, stats):
    # Same approach as above, but without retries.
    with cleanup_db.engine.connect() as conn:
        with conn.begin() as trans:
            conn.execute(insert(User), [{'token': 'foo'}])

            orig_upload_data = upload._upload_data
            num = 0

            def mock_upload_data(task, user_token, data, _lock_timeout=100):
                nonlocal num
                num += 1
                return orig_upload_data(task, user_token, data,
                                        _lock_timeout=_lock_timeout)

            with mock.patch.object(upload, '_upload_data', mock_upload_data):
                with db.session(commit=False) as session:
                    task = DummyTask(bloom_domain=bloom_domain, db=db,
                                     raven=raven, stats=stats)
                    assert not upload.upload_data(
                        task, 'foo', _PAYLOAD,
                        _lock_timeout=100, _retry_wait=0.01, _retries=0)
                    raven.check(['OperationalError'])
                    assert num == 1
                    assert session.query(User).count() == 0
                    assert session.query(Session).count() == 0
            trans.rollback()


class TestUpload(object):

    def test_task(self, celery, crypto, stats):
        assert tasks.upload.delay(
            'foo', crypto.encrypt(json.dumps(_COMBINED_PAYLOAD))).get()

        stats.check(counter=[
            ('data.url.drop', 1, 1),
            ('data.session.drop', 1, 2),
        ])

    def test_task_fail(self, celery, crypto, stats):
        assert not tasks.upload.delay(
            'foo', crypto.encrypt(b'no json')).get()

        assert not tasks.upload.delay(
            'foo', crypto.encrypt(b'{"sessions": [{}]}')).get()

        stats.check(counter=[
            ('data.session.drop', 1),
            ('data.upload.error', 1, ['reason:json']),
            ('data.upload.error', 1, ['reason:validation']),
        ])
