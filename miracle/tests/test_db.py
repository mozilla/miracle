from sqlalchemy import text

from miracle.db import create_db


def test_db(db):
    with db.session() as session:
        session.execute(text('create table foo (num integer)'))
        session.execute(text('insert into foo (num) values (1)'))
        session.commit()
        res = session.execute(text('select num from foo')).fetchall()
        assert res == [(1, )]


def test_ping(db, raven):
    assert db.ping(raven)

    try:
        broken_db = create_db(
            'postgresql+psycopg2://user:pass@127.0.0.1:9/none')
        assert not broken_db.ping(raven)
    finally:
        broken_db.close()

    raven.check(['OperationalError'])


def test_isolated(db):
    # Create the same table as in test_db, to ensure test functions
    # are isolated from each other.
    with db.session() as session:
        session.execute(text('create table foo (num integer)'))
        session.commit()
