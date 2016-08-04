from alembic import context

from miracle.db import create_db
from miracle.log import configure_logging


def run_migrations_online(_db=None):
    db = create_db(_db=_db)
    with db.engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

configure_logging()
run_migrations_online()
