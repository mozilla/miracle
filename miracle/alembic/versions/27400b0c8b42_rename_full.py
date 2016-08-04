"""Rename URL full column.

Revision ID: 27400b0c8b42
Revises: 88d1704f1aef
Create Date: 2016-08-04 12:30:00.000000
"""

import logging

from alembic import op
import sqlalchemy as sa

log = logging.getLogger('alembic.migration')
revision = '27400b0c8b42'
down_revision = '88d1704f1aef'


def upgrade():
    log.info('Rename URL full column.')
    stmt = 'ALTER TABLE urls RENAME COLUMN "full" TO url'
    op.execute(sa.text(stmt))

    stmt = 'ALTER TABLE urls RENAME CONSTRAINT urls_full_key TO urls_url_key'
    op.execute(sa.text(stmt))

    log.info('Add indices on sessions foreign keys.')
    stmt = 'DROP INDEX sessions_user_id_start_time_idx'
    op.execute(sa.text(stmt))

    stmt = '''\
CREATE INDEX sessions_url_id_idx ON sessions USING btree (url_id)'''
    op.execute(sa.text(stmt))

    stmt = '''\
CREATE INDEX sessions_user_id_idx ON sessions USING btree (user_id)'''
    op.execute(sa.text(stmt))


def downgrade():
    log.info('Revert URL full column renaming.')
    stmt = 'ALTER TABLE urls RENAME COLUMN url TO "full"'
    op.execute(sa.text(stmt))

    stmt = 'ALTER TABLE urls RENAME CONSTRAINT urls_url_key TO urls_full_key'
    op.execute(sa.text(stmt))

    log.info('Remove indices from sessions foreign keys.')
    stmt = '''\
CREATE INDEX sessions_user_id_start_time_idx
ON sessions USING btree (user_id, start_time)
'''
    op.execute(sa.text(stmt))

    stmt = 'DROP INDEX sessions_url_id_idx'
    op.execute(sa.text(stmt))

    stmt = 'DROP INDEX sessions_user_id_idx'
    op.execute(sa.text(stmt))
