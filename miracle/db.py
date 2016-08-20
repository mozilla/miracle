from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from miracle.config import DB_URI

# Side-effect import which registers all models.
from miracle.models import Model  # NOQA


def create_db(db_uri=DB_URI, _db=None):
    if _db is not None:
        return _db
    return Database(db_uri)


class Database(object):

    def __init__(self, db_uri):
        options = {
            'pool_recycle': 3600,
            'pool_size': 10,
            'pool_timeout': 10,
            'max_overflow': 10,
            'echo': False,
        }
        self.db_uri = db_uri
        self.engine = create_engine(db_uri, **options)
        self.session_factory = sessionmaker(bind=self.engine)

    def close(self):
        self.engine.pool.dispose()

    def ping(self, raven):
        try:
            with self.session(commit=False) as session:
                res = session.execute('select 1')
                res.fetchall()
                res.close()
        except Exception:
            raven.captureException()
            return False
        return True

    @contextmanager
    def session(self, commit=True):
        try:
            session = self.session_factory()
            yield session
            if commit:
                session.commit()
        except Exception:  # pragma: no cover
            session.rollback()
            raise
        finally:
            session.close()
