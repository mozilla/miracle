"""Add session tables.

Revision ID: 1bdf1028a085
Revises: 4b11500c9014
Create Date: 2016-07-14 18:05:00.000000
"""

import logging

from alembic import op
import sqlalchemy as sa

log = logging.getLogger('alembic.migration')
revision = '1bdf1028a085'
down_revision = '4b11500c9014'


def upgrade():
    log.info('Initialize database.')

    log.info('Add session tables.')
    url_stmt = '''\
CREATE TABLE url (
    id bigint NOT NULL,
    "full" character varying(2048) NOT NULL,
    hostname character varying(256),
    scheme character varying(8)
);
CREATE SEQUENCE url_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE url_id_seq OWNED BY url.id;
ALTER TABLE ONLY url
    ALTER COLUMN id SET DEFAULT nextval('url_id_seq'::regclass);
ALTER TABLE ONLY url
    ADD CONSTRAINT url_pkey PRIMARY KEY (id);
ALTER TABLE ONLY url
    ADD CONSTRAINT url_full_key UNIQUE ("full");
CREATE INDEX url_hostname_idx ON url USING btree (hostname);
CREATE INDEX url_scheme_idx ON url USING btree (scheme);
'''

    user_stmt = '''\
CREATE TABLE "user" (
    id integer NOT NULL,
    token character varying(36) NOT NULL
);
CREATE SEQUENCE user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE user_id_seq OWNED BY "user".id;
ALTER TABLE ONLY "user"
    ALTER COLUMN id SET DEFAULT nextval('user_id_seq'::regclass);
ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);
ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_token_key UNIQUE (token);
'''

    session_stmt = '''\
CREATE TABLE session (
    id bigint NOT NULL,
    url_id bigint,
    user_id integer,
    start_time timestamp without time zone NOT NULL,
    duration integer
);
CREATE SEQUENCE session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE session_id_seq OWNED BY session.id;
ALTER TABLE ONLY session
    ALTER COLUMN id SET DEFAULT nextval('session_id_seq'::regclass);
ALTER TABLE ONLY session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);
ALTER TABLE ONLY session
    ADD CONSTRAINT session_url_id_fkey
    FOREIGN KEY (url_id) REFERENCES url(id) ON DELETE CASCADE;
ALTER TABLE ONLY session
    ADD CONSTRAINT session_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE;
CREATE INDEX session_user_id_start_time_idx
    ON session USING btree (user_id, start_time);
'''
    op.execute(sa.text(url_stmt))
    op.execute(sa.text(user_stmt))
    op.execute(sa.text(session_stmt))


def downgrade():
    log.info('Drop session tables.')
    stmt = '''\
DROP TABLE "session" CASCADE;
DROP TABLE "url" CASCADE;
DROP TABLE "user" CASCADE;
'''
    op.execute(sa.text(stmt))
