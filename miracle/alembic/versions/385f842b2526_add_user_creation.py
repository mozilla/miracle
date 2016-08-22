"""Add user creation date.

Revision ID: 385f842b2526
Revises: 27400b0c8b42
Create Date: 2016-08-22 17:00:00.000000
"""

import logging

from alembic import op
import sqlalchemy as sa

log = logging.getLogger('alembic.migration')
revision = '385f842b2526'
down_revision = '27400b0c8b42'


def upgrade():
    log.info('Add user creation date.')
    stmt = '''\
ALTER TABLE users
ADD COLUMN created TIMESTAMP WITHOUT TIME ZONE'''
    op.execute(sa.text(stmt))


def downgrade():
    log.info('Drop user creation date.')
    stmt = 'ALTER TABLE users DROP COLUMN created'
    op.execute(sa.text(stmt))
