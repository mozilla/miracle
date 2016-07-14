"""Initialize database.

Revision ID: 4b11500c9014
Revises: None
Create Date: 2016-07-14 18:05:00.000000
"""

import logging

log = logging.getLogger('alembic.migration')
revision = '4b11500c9014'
down_revision = None


def upgrade():
    log.info('Initialize database.')


def downgrade():
    log.info('Cleanup database.')
