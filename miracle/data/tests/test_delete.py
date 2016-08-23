from datetime import datetime

from miracle.data import delete
from miracle.data import tasks
from miracle.models import (
    URL,
    User,
    Session,
)

TEST_TIME = datetime.utcfromtimestamp(1469400000)


class DummyTask(object):

    def __init__(self, db=None, stats=None):
        self.db = db
        self.stats = stats


def test_delete_urls(db, stats):
    with db.session(commit=False) as session:
        url1 = URL(**URL.from_url('http://foo.com'))
        url2 = URL(**URL.from_url('http://bar.com'))
        url3 = URL(**URL.from_url('http://baz.com'))
        user1 = User(token='user1', created=TEST_TIME)
        user2 = User(token='user2', created=TEST_TIME)
        session.add_all([
            Session(url=url1, user=user1, start_time=TEST_TIME),
            Session(url=url1, user=user2, start_time=TEST_TIME),
            Session(url=url2, user=user1, start_time=TEST_TIME),
            url3,
        ])
        session.commit()

        task = DummyTask(db=db, stats=stats)
        assert delete.delete_urls(task, [url1.id, url2.id, url3.id]) == 1

        assert session.query(URL).count() == 2
        assert session.query(User).count() == 2
        assert session.query(Session).count() == 3


def test_delete_user(db, stats):
    with db.session(commit=False) as session:
        url1 = URL(**URL.from_url('http://foo.com'))
        url2 = URL(**URL.from_url('http://bar.com'))
        url3 = URL(**URL.from_url('http://baz.com'))
        user1 = User(token='user1', created=TEST_TIME)
        user2 = User(token='user2', created=TEST_TIME)
        session.add_all([
            Session(url=url1, user=user1, start_time=TEST_TIME),
            Session(url=url2, user=user1, start_time=TEST_TIME),
            Session(url=url2, user=user2, start_time=TEST_TIME),
            Session(url=url3, user=user2, start_time=TEST_TIME),
        ])
        session.commit()

        task = DummyTask(db=db, stats=stats)
        deleted_user, url_ids = delete.delete_user(task, 'user1')
        assert deleted_user
        assert set(url_ids) == {url1.id, url2.id}

        assert session.query(URL).count() == 3
        assert session.query(User).count() == 1
        assert session.query(Session).count() == 2

        # Second delete of the same user.
        assert delete.delete_user(task, 'user1') == (False, [])

    stats.check(counter=[
        ('data.user.delete', 1),
    ], timer=[
        ('data.user.delete_hours', 1),
    ])


def test_delete_urls_main(db, stats):
    def _delete(task, url_ids):
        return url_ids

    task = DummyTask(db=db, stats=stats)
    result = delete.delete_urls_main(task, [1, 2], _delete_urls=_delete)
    assert set(result) == {1, 2}


def test_delete_user_main(db, stats):
    with db.session(commit=False) as session:
        url = URL(**URL.from_url('http://foo.com'))
        user = User(token='user1', created=TEST_TIME)
        session.add(Session(url=url, user=user, start_time=TEST_TIME))
        session.commit()

        def _delete(task, user):
            return (user, [url.id])

        task = DummyTask(db=db, stats=stats)
        result = delete.delete_user_main(
            task, 'foo', tasks.delete_urls, _delete_user=_delete)
        assert result == 'foo'
        assert session.query(URL).count() == 1

        stats.check(timer=[
            ('task', 1, ['task:data.tasks.delete_urls']),
        ])


def test_delete_urls_task(celery):
    assert tasks.delete_urls.delay([1], _delete_urls=False).get()
    assert not tasks.delete_urls.delay([], _delete_urls=False).get()


def test_delete_user_task(celery):
    assert tasks.delete.delay('foo', _delete_user=False).get()
    assert not tasks.delete.delay('', _delete_user=False).get()
