from datetime import datetime

from miracle.models.session import (
    URL,
    User,
    Session,
)


def test_url(db):
    value = 'https://www.example.com:80/path?query=foo'
    with db.session(commit=False) as session:
        session.add(URL.from_url(value))
        session.commit()

        url = session.query(URL).first()
        assert isinstance(url.id, int)
        assert url.full == value
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
    value = 'https://example.com/path?query=foo'
    start = datetime.utcfromtimestamp(1469400000)

    with db.session(commit=False) as session:
        url = URL.from_url(value)
        user = User(token='foo')
        session.add(Session(
            user=user, url=url, start_time=start, duration=2400))
        session.commit()

        sess = session.query(Session).first()
        assert isinstance(sess.id, int)
        assert sess.start_time == start
        assert sess.duration == 2400

        # deleting the user, deletes all sessions
        session.query(User).filter(User.token == 'foo').delete()
        session.commit()
        assert not session.query(Session).count()
