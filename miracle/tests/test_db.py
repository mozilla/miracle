from sqlalchemy import text


def test_db(db):
    with db.session() as session:
        session.execute(text('create table foo (num integer)'))
        session.execute(text('insert into foo (num) values (1)'))
        session.commit()
        res = session.execute(text('select num from foo')).fetchall()
        assert res == [(1, )]


def test_ping(db, raven):
    assert db.ping(raven)
