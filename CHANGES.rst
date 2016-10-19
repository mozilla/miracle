=========
Changelog
=========

1.1.8 (unreleased)
==================



1.1.7 (2016-10-19)
==================

- Validate DNS resolution for hostnames.

- Drop sessions with a start_time in the future or more than 2 weeks old.

- Add script to calculate daily sessions per user.

- Re-factor `scripts.analysis` into a new sub-package.

- Test our bloom filter against the top 100 domains.


1.1.6 (2016-10-05)
==================

- Filter out users who have not participated for at least a week from
  the weekly recurrence analysis script.


1.1.5 (2016-09-20)
==================

- Filter out non-standard HTTP/S ports.

- Increase maximum valid session duration to 21 days.

- Filter out invalid domain names and IP addresses.

- Filter out all `.local` domains.

- Use `time.monotonic` to capture timing information.


1.1.4 (2016-09-16)
==================

- Extend domain blocklist to block certain top-level domains.

- Add tab_id to upload schema and extend sessions table.

- Capture and retry SQLAlchemy internal TypeError during upload.

- Adjust miracle_block script to take public suffixes into account.

- Apply domain blocklist based on domain's public suffix.

- Add public suffix list (2016-09-14).

- Extend domain blocklist.


1.1.3 (2016-09-13)
==================

- Fix user header parsing.

- Update end date based on launch data.


1.1.2 (2016-09-07)
==================

- #2: Add analysis script to get recurring URL stats.

- Extend Redis ping by testing a write operation.

- Remove unused AWS S3 bucket code.

- Check user header against allowed character list.

- Speed up orphaned URL deletion.


1.1.1 (2016-08-23)
==================

- Validate JWE structure in HTTP upload API.

- Remove orphaned URLs after user deletion.

- #4: Add a end date for the experiment.

- Add ``data.user.delete_hours`` metric to track user participation time.

- Add creation date to users table.

- Emit HSTS headers and add CSP for the homepage.

- Correct CORS headers for jwk and stats HTTP APIs.

- Enforce SSL for database connections.


1.1.0 (2016-08-19)
==================

- Remove support for GZIP encoded upload requests.

- Change the upload API to expect a JWE encrypted body.

- Change crypto helper module to use JWE RSA-OAEP/A256GCM encryption.

- Add crypto helper module for RSA-OAEP based encryption.

- Update Python dependencies and add new cryptography dependency.


1.0.9 (2016-08-08)
==================

- Add a `/v1/stats` API endpoint.

- Use uritools for URL splitting.


1.0.8 (2016-08-05)
==================

- Use tags for `data.upload.error` metrics.

- No longer set up a DB connection from the web app.

- Capture exceptions in the startup process and send them to Sentry.


1.0.7 (2016-08-04)
==================

- Add help messages and progress logging to command line scripts.

- Database migration, renaming "full" column and optimizing indices.

- Set up logging for alembic migrations.


1.0.6 (2016-08-03)
==================

- Database migration, pluralizing all table names.

- Add a miracle_block script to remove blocklisted URLs from the database.


1.0.5 (2016-08-03)
==================

- Add and use domain blocklist.

- Add Hydra Bloom filter library.

- Use bulk inserts and upserts in session upload task.

- Add a link to project description on the homepage.


1.0.4 (2016-07-29)
==================

- Filter out URLs containing private IP addresses.

- Filter out non-HTTP/S URLs.

- Provide pre-compiled wheels for binary Python dependencies.


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
