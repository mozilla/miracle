from datetime import datetime, timedelta

from miracle.analysis import daily_sessions
from miracle.models import (
    Session,
    URL,
    User,
)

NOW = datetime.utcnow()
PAST = NOW - timedelta(days=20)
YESTERDAY = NOW - timedelta(days=1)
TWO_DAYS = NOW - timedelta(days=2)


def test_main(db):
    assert daily_sessions.main(db) is None


def test_daily_sessions(db):
    with db.session() as session:
        url = URL(**URL.from_url('https://example.com/'))
        user1 = User(token='user1', created=PAST)
        user2 = User(token='user2', created=PAST)
        user3 = User(token='user3', created=PAST)
        session.add_all([
            # User 1
            Session(url=url, user=user1, start_time=NOW),
            Session(url=url, user=user1, start_time=NOW),
            Session(url=url, user=user1, start_time=NOW),
            Session(url=url, user=user1, start_time=YESTERDAY),
            Session(url=url, user=user1, start_time=YESTERDAY),
            Session(url=url, user=user1, start_time=TWO_DAYS),
            Session(url=url, user=user1, start_time=TWO_DAYS),
            # User 2
            Session(url=url, user=user2, start_time=NOW),
            Session(url=url, user=user2, start_time=YESTERDAY),
            Session(url=url, user=user2, start_time=TWO_DAYS),
            # User 3
            Session(url=url, user=user3, start_time=NOW),
        ])
        session.flush()
        assert daily_sessions.daily_sessions(db) == (
            'max: 3', 'mean: 2', 'median: 1', 'min: 1')
