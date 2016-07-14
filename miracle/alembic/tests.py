from alembic.autogenerate import compare_metadata
from alembic import command as alembic_command
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
import pytest
from sqlalchemy.schema import MetaData

from miracle.config import ALEMBIC_CFG
from miracle.conftest import (
    setup_db,
    teardown_db,
)

SQL_BASE = '''\
CREATE TABLE alembic_version (
  version_num varchar(32) NOT NULL
);
'''


@pytest.yield_fixture(scope='function')
def fresh_db(global_db):
    yield global_db
    teardown_db(global_db.engine)
    setup_db(global_db.engine)
    global_db.close()


def current_db_revision(engine):
    with engine.connect() as conn:
        result = conn.execute('select version_num from alembic_version')
        alembic_rev = result.first()
    return None if alembic_rev is None else alembic_rev[0]


def test_migration(fresh_db):
    engine = fresh_db.engine
    # capture state of fresh database
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # delete all tables
    teardown_db(engine)

    # setup old database schema
    with engine.connect() as conn:
        conn.execute(SQL_BASE)

    # we have no alembic base revision
    assert current_db_revision(engine) is None

    # run the migration
    with engine.connect() as conn:
        trans = conn.begin()
        alembic_command.upgrade(ALEMBIC_CFG, 'head')
        trans.commit()

    # afterwards the DB is stamped
    db_revision = current_db_revision(engine)
    assert db_revision is not None

    # db revision matches latest alembic revision
    alembic_script = ScriptDirectory.from_config(ALEMBIC_CFG)
    alembic_head = alembic_script.get_current_head()
    assert db_revision == alembic_head

    # compare the db schema from a migrated database to
    # one created fresh from the model definitions
    opts = {
        'compare_server_default': True,
    }
    with engine.connect() as conn:
        context = MigrationContext.configure(connection=conn, opts=opts)
        metadata_diff = compare_metadata(context, metadata)

    assert metadata_diff == []

    # downgrade back to the beginning
    with engine.connect() as conn:
        trans = conn.begin()
        alembic_command.downgrade(ALEMBIC_CFG, 'base')
        trans.commit()
