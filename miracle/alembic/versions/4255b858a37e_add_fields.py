"""Add various fields.

Revision ID: 4255b858a37e
Revises: 385f842b2526
Create Date: 2016-09-16 07:30:00
"""

import logging

from alembic import op
import sqlalchemy as sa

log = logging.getLogger('alembic.migration')
revision = '4255b858a37e'
down_revision = '385f842b2526'


def upgrade():
    log.info('Add tab_id to sessions.')
    stmt = '''\
ALTER TABLE sessions
ADD COLUMN tab_id character varying(32)'''
    op.execute(sa.text(stmt))


def downgrade():
    log.info('Drop tab_id from sessions.')
    stmt = 'ALTER TABLE sessions DROP COLUMN tab_id'
    op.execute(sa.text(stmt))
