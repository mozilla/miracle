from datetime import datetime
import os

from miracle.models import (
    Session,
    URL,
    User,
)
from miracle.scripts import block

TEST_START = datetime.utcfromtimestamp(1469400000)


def test_remove_urls(db):
    # Test without any matching URLs
    assert block.remove_urls(db, ['localhost']) == 0

    with db.session() as session:
        url1 = URL(**URL.from_url('http://localhost:80/path'))
        url2 = URL(**URL.from_url('https://localhost/'))
        url3 = URL(**URL.from_url('https://example.com/'))
        user1 = User(token='user1')
        user2 = User(token='user2')
        user3 = User(token='user3')
        session.add_all([
            Session(user=user1, url=url1, start_time=TEST_START),
            Session(user=user1, url=url2, start_time=TEST_START),
            Session(user=user1, url=url3, start_time=TEST_START),
            Session(user=user2, url=url1, start_time=TEST_START),
            Session(user=user3, url=url3, start_time=TEST_START),
        ])
    assert block.remove_urls(db, ['localhost']) == 2

    with db.session() as session:
        hostnames = {row[0] for row in session.query(URL.hostname).all()}
        assert hostnames == {'example.com'}

        sessions = session.query(Session).all()
        assert {(sess.user.token, sess.url.hostname) for sess in sessions} == \
            {('user1', 'example.com'), ('user3', 'example.com')}


def test_main(db, tmp_path):
    in_filename = os.path.join(tmp_path, 'bloom.txt')
    with open(in_filename, 'wt') as fd:
        fd.write('localhost\n')

    assert block.main(db, filename=in_filename) == 0
