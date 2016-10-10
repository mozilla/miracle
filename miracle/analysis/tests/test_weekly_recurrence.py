from datetime import datetime, timedelta

from miracle.models import (
    Session,
    URL,
    User,
)
from miracle.analysis import weekly_recurrence

NOW = datetime.utcnow()
USER_CREATED = NOW - timedelta(days=20)
TEST_START = NOW - timedelta(days=14)


def test_main(db):
    assert weekly_recurrence.main(db) is None


def test_weekly_recurrence(db):
    with db.session() as session:
        url1 = URL(**URL.from_url('http://localhost:80/path'))
        url2 = URL(**URL.from_url('https://localhost/'))
        url3 = URL(**URL.from_url('https://example.com/'))
        url4 = URL(**URL.from_url('https://example.com/other'))
        user1 = User(token='user1', created=USER_CREATED)
        user2 = User(token='user2', created=USER_CREATED)
        user3 = User(token='user3', created=NOW)
        # Fourth user without any sessions
        session.add(User(token='user4', created=USER_CREATED))
        session.add_all([
            # URL visited three times in a week
            Session(user=user1, url=url1, start_time=TEST_START),
            Session(user=user1, url=url1,
                    start_time=TEST_START + timedelta(days=1)),
            Session(user=user1, url=url1,
                    start_time=TEST_START + timedelta(days=2)),
            # URL visited three times, but not in a week
            Session(user=user1, url=url2, start_time=TEST_START),
            Session(user=user1, url=url2,
                    start_time=TEST_START + timedelta(days=1)),
            Session(user=user1, url=url2,
                    start_time=TEST_START + timedelta(days=8)),
            # URL visited less than three times
            Session(user=user1, url=url3, start_time=TEST_START),
            Session(user=user1, url=url3,
                    start_time=TEST_START + timedelta(days=1)),
            # URL visited three times, in two distinct weeks
            Session(user=user1, url=url4, start_time=TEST_START),
            Session(user=user1, url=url4,
                    start_time=TEST_START + timedelta(days=1)),
            Session(user=user1, url=url4,
                    start_time=TEST_START + timedelta(days=2)),
            Session(user=user1, url=url4,
                    start_time=TEST_START + timedelta(days=10)),
            Session(user=user1, url=url4,
                    start_time=TEST_START + timedelta(days=11)),
            Session(user=user1, url=url4,
                    start_time=TEST_START + timedelta(days=12)),
            # Second user with too few sessions
            Session(user=user2, url=url3, start_time=TEST_START),
            Session(user=user2, url=url3,
                    start_time=TEST_START + timedelta(days=8)),
            # Third user with too little participation time
            Session(user=user3, url=url3, start_time=TEST_START),
            Session(user=user3, url=url3,
                    start_time=TEST_START + timedelta(days=1)),
            Session(user=user3, url=url3,
                    start_time=TEST_START + timedelta(days=10)),
        ])
        session.flush()
        assert weekly_recurrence.weekly_recurrence(db) == (
            [(0, 1), (2, 1)], ('max: 2', 'mean: 1', 'median: 1', 'min: 0'))
