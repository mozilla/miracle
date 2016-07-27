from datetime import datetime

from miracle.data import delete
from miracle.data import tasks
from miracle.models import (
    URL,
    User,
    Session,
)

TEST_START = datetime.utcfromtimestamp(1469400000)


class DummyTask(object):

    def __init__(self, db=None):
        self.db = db


def test_delete_data(db):
    with db.session(commit=False) as session:
        url = URL.from_url('http://example.com')
        user = User(token='foo')
        session.add(Session(url=url, user=user, start_time=TEST_START))
        session.commit()

        task = DummyTask(db=db)
        assert delete.delete_data(task, 'foo')

        assert session.query(User).count() == 0
        assert session.query(Session).count() == 0


def test_delete_main(db):
    def _delete(task, user):
        return user

    task = DummyTask(db=db)
    result = delete.main(task, 'foo', _delete_data=_delete)
    assert result == 'foo'


def test_task(celery):
    assert tasks.delete.delay('foo', _delete_data=False).get()


def test_task_fail(celery):
    assert not tasks.delete.delay('', _delete_data=False).get()
