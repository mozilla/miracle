=========
Changelog
=========

1.0.3 (2016-07-28)
==================

- Pin Python requirements to specific hashes.

- Split Python requirements into build, binary and pure-python files.

- Add quantitative metrics about the incoming data.

- Remove stackframe content and exception values from Sentry.

- Retry database insertion on conflict errors.

- Store and delete session data into and from database.

- Add url, user and session database tables.


1.0.2 (2016-07-26)
==================

- Move JSON decoding from web app to backend celery tier.

- Document alembic and make it more easily accessible.

- Add alembic migrations scaffold.

- Add Postgres database to the stack.

- Rename to miracle.


1.0.1 (2016-06-06)
==================

- Fix bucket access check.


1.0 (2016-06-01)
================

- Initial version.
