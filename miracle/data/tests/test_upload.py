from datetime import datetime
import json

from miracle.data import tasks
from miracle.data import upload
from miracle.models import (
    URL,
    User,
    Session,
)

TEST_START = datetime.utcfromtimestamp(1469400000)
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
    {
        "duration": 6200,
        "start_time": 1469500000,
        "url": "https://www.foo.com/",
    },
]}
_PAYLOAD_DURATIONS = {sess['duration'] for sess in _PAYLOAD['sessions']}
_PAYLOAD_STARTS = {datetime.utcfromtimestamp(sess['start_time'])
                   for sess in _PAYLOAD['sessions']}
_PAYLOAD_URLS = {sess['url'] for sess in _PAYLOAD['sessions']}


class DummyTask(object):

    def __init__(self, db=None):
        self.db = db


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


def test_upload_data_new_user(db):
    with db.session(commit=False) as session:
        url = URL.from_url('http://www.example.com/')
        session.add(url)
        session.commit()

        task = DummyTask(db=db)
        assert upload.upload_data(task, 'foo', _PAYLOAD)

        assert session.query(URL).count() == 4
        users = session.query(User).all()
        assert len(users) == 1
        assert users[0].token == 'foo'

        sessions = session.query(Session).all()
        assert len(sessions) == 5
        assert {sess.duration for sess in sessions} == _PAYLOAD_DURATIONS
        assert {sess.start_time for sess in sessions} == _PAYLOAD_STARTS
        assert {sess.url.full for sess in sessions} == _PAYLOAD_URLS


def test_upload_data_existing_user(db):
    with db.session(commit=False) as session:
        user = User(token='foo')
        session.add(user)
        session.commit()

        task = DummyTask(db=db)
        assert upload.upload_data(task, 'foo', _PAYLOAD)

        assert session.query(URL).count() == 4
        users = session.query(User).all()
        assert len(users) == 1
        assert users[0].id == user.id
        assert users[0].token == 'foo'

        sessions = session.query(Session).all()
        assert len(sessions) == 5
        assert {sess.duration for sess in sessions} == _PAYLOAD_DURATIONS
        assert {sess.start_time for sess in sessions} == _PAYLOAD_STARTS
        assert {sess.url.full for sess in sessions} == _PAYLOAD_URLS


def test_upload_data_duplicated_sessions(db):
    with db.session(commit=False) as session:
        task = DummyTask(db=db)
        assert upload.upload_data(task, 'foo', _PAYLOAD)
        assert upload.upload_data(task, 'foo', _PAYLOAD)
        assert session.query(Session).count() == 10


def test_upload_main(db):
    def _upload(task, user, data):
        return (user, data)

    task = DummyTask(db=db)
    result = upload.main(
        task, 'foo', json.dumps(_PAYLOAD), _upload_data=_upload)
    assert result == ('foo', _PAYLOAD)


def test_task(celery):
    assert tasks.upload.delay(
        'foo', json.dumps(_PAYLOAD).encode('utf-8'), _upload_data=False).get()


def test_task_fail(celery):
    assert not tasks.upload.delay(
        'foo', b'no json', _upload_data=False).get()
