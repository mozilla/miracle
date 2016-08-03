"""Pluralize table names.

Revision ID: 88d1704f1aef
Revises: 1bdf1028a085
Create Date: 2016-08-03 22:30:00.000000
"""

import logging

from alembic import op
import sqlalchemy as sa

log = logging.getLogger('alembic.migration')
revision = '88d1704f1aef'
down_revision = '1bdf1028a085'


def upgrade():
    log.info('Drop singular tables.')
    stmt = '''\
DROP TABLE "session" CASCADE;
DROP TABLE "url" CASCADE;
DROP TABLE "user" CASCADE;
'''
    op.execute(sa.text(stmt))

    log.info('Add pluralized tables.')
    url_stmt = '''\
CREATE TABLE urls (
    id bigint NOT NULL,
    "full" character varying(2048) NOT NULL,
    hostname character varying(256),
    scheme character varying(8)
);
CREATE SEQUENCE urls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE urls_id_seq OWNED BY urls.id;
ALTER TABLE ONLY urls
    ALTER COLUMN id SET DEFAULT nextval('urls_id_seq'::regclass);
ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_pkey PRIMARY KEY (id);
ALTER TABLE ONLY urls
    ADD CONSTRAINT urls_full_key UNIQUE ("full");
CREATE INDEX urls_hostname_idx ON urls USING btree (hostname);
CREATE INDEX urls_scheme_idx ON urls USING btree (scheme);
'''

    user_stmt = '''\
CREATE TABLE users (
    id integer NOT NULL,
    token character varying(36) NOT NULL
);
CREATE SEQUENCE users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE users_id_seq OWNED BY users.id;
ALTER TABLE ONLY users
    ALTER COLUMN id SET DEFAULT nextval('users_id_seq'::regclass);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
ALTER TABLE ONLY users
    ADD CONSTRAINT users_token_key UNIQUE (token);
'''

    session_stmt = '''\
CREATE TABLE sessions (
    id bigint NOT NULL,
    url_id bigint,
    user_id integer,
    start_time timestamp without time zone NOT NULL,
    duration integer
);
CREATE SEQUENCE sessions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE sessions_id_seq OWNED BY sessions.id;
ALTER TABLE ONLY sessions
    ALTER COLUMN id SET DEFAULT nextval('sessions_id_seq'::regclass);
ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);
ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_url_id_fkey
    FOREIGN KEY (url_id) REFERENCES urls(id) ON DELETE CASCADE;
ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
CREATE INDEX sessions_user_id_start_time_idx
    ON sessions USING btree (user_id, start_time);
'''
    op.execute(sa.text(url_stmt))
    op.execute(sa.text(user_stmt))
    op.execute(sa.text(session_stmt))


def downgrade():
    log.info('Drop pluralized tables.')
    stmt = '''\
DROP TABLE sessions CASCADE;
DROP TABLE urls CASCADE;
DROP TABLE users CASCADE;
'''
    op.execute(sa.text(stmt))

    log.info('Add singular tables.')
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
