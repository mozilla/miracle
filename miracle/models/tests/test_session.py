from datetime import datetime

from miracle.models.session import (
    URL,
    User,
    Session,
)

TEST_START = datetime.utcfromtimestamp(1469400000)
TEST_URL = 'https://www.example.com:80/path?query=foo'
TEST_URL2 = 'https://example.com/something/else'


def test_url(db):
    with db.session(commit=False) as session:
        session.add(URL.from_url(TEST_URL))
        session.commit()

        url = session.query(URL).first()
        assert isinstance(url.id, int)
        assert url.full == TEST_URL
        assert url.scheme == 'https'
        assert url.hostname == 'www.example.com'
        assert url.sessions.all() == []


def test_user(db):
    with db.session(commit=False) as session:
        session.add(User(token='abc'))
        session.commit()

        user = session.query(User).first()
        assert isinstance(user.id, int)
        assert user.token == 'abc'
        assert user.sessions.all() == []


def test_session(db):
    with db.session(commit=False) as session:
        url = URL.from_url(TEST_URL)
        user = User(token='foo')
        session.add(Session(
            user=user, url=url, start_time=TEST_START, duration=2400))
        session.commit()

        sess = session.query(Session).first()
        assert isinstance(sess.id, int)
        assert sess.start_time == TEST_START
        assert sess.duration == 2400

        # Deleting a session, leaves the user and URL untouched
        session.query(Session).delete()
        session.commit()
        assert session.query(URL).count() == 1
        assert session.query(User).count() == 1


def test_session_url_delete(db):
    with db.session(commit=False) as session:
        url1 = URL.from_url(TEST_URL)
        url2 = URL.from_url(TEST_URL2)
        user = User(token='foo')
        session.add(Session(
            user=user, url=url1, start_time=TEST_START, duration=1000))
        session.add(Session(
            user=user, url=url2, start_time=TEST_START, duration=2000))
        session.commit()

        # Deleting a URL, deletes all the URL's sessions
        session.query(URL).filter(URL.id == url1.id).delete()
        session.commit()
        sessions = session.query(Session).all()
        assert len(sessions) == 1
        assert sessions[0].url_id == url2.id


def test_session_user_delete(db):
    with db.session(commit=False) as session:
        url = URL.from_url(TEST_URL)
        user1 = User(token='foo')
        user2 = User(token='bar')
        session.add(Session(
            user=user1, url=url, start_time=TEST_START, duration=1000))
        session.add(Session(
            user=user2, url=url, start_time=TEST_START, duration=2000))
        session.commit()

        # Deleting the user, deletes all the user's sessions
        session.query(User).filter(User.id == user1.id).delete()
        session.commit()
        sessions = session.query(Session).all()
        assert len(sessions) == 1
        assert sessions[0].user_id == user2.id
