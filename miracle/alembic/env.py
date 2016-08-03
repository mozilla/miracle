from logging.config import fileConfig

from alembic import context

from miracle.db import create_db

config = context.config
if config.config_file_name:  # pragma: no cover
    fileConfig(config.config_file_name)


def run_migrations_online(_db=None):
    db = create_db(_db=_db)
    with db.engine.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
