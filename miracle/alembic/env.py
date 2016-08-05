from alembic import context

from miracle.db import create_db
from miracle.log import (
    configure_logging,
    create_raven,
)


def run_migrations_online():
    raven = create_raven()
    # Send a raven message to implicitly register the current release
    # with Sentry.
    raven.captureMessage('Running alembic.')
    try:
        db = create_db()
        with db.engine.connect() as connection:
            context.configure(connection=connection)
            with context.begin_transaction():
                context.run_migrations()
    except Exception:  # pragma: no cover
        raven.captureException()
        raise


configure_logging()
run_migrations_online()
