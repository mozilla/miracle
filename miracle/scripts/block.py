import argparse
import os
import sys

from sqlalchemy import (
    delete,
    select,
)

from miracle.bloom import read_source
from miracle.config import BLOOM_DOMAIN_SOURCE
from miracle.db import create_db
from miracle.log import (
    configure_logging,
    LOGGER,
)
from miracle.models import URL


def remove_urls(db, lines):
    found_url_ids = []
    with db.session(commit=False) as session:
        # Get a list of URL ids to delete in larger batches.
        for i in range(0, len(lines), 100):
            name_batch = lines[i:i + 100]
            if name_batch:
                rows = session.execute(
                    select([URL.id]).where(
                        URL.hostname.in_(name_batch))).fetchall()
                if rows:
                    found_url_ids.extend([row[0] for row in rows])

    LOGGER.info('Found %s domains in database.', len(found_url_ids))
    if not found_url_ids:
        return 0

    actually_deleted = 0
    found_url_ids.sort()
    batches = ((len(found_url_ids) - 1) // 10) + 1
    LOGGER.info('Deleting domains in batches of 10.')
    for i in range(0, len(found_url_ids), 10):
        # Delete URLs by id in small transactional batches, as these
        # can result in large numbers of sessions to be deleted at the
        # same time.
        id_batch = found_url_ids[i:i + 10]
        if id_batch:
            LOGGER.info('Deleting domains, batch %s of %s.',
                        i // 10 + 1, batches)
            with db.session() as session:
                res = session.execute(delete(URL).where(URL.id.in_(id_batch)))
                actually_deleted += res.rowcount

    return actually_deleted


def main(db, filename=BLOOM_DOMAIN_SOURCE):
    LOGGER.info('Reading source file: %s', filename)
    lines = read_source(filename)
    LOGGER.info('Found %s domains in source file.', len(lines))
    urls_removed = remove_urls(db, lines)
    LOGGER.info('Deleted %s domains.', urls_removed)
    return urls_removed


def console_entry():  # pragma: no cover
    configure_logging()
    argv = sys.argv

    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Remove blocklisted domains from the database.')
    parser.add_argument('filename',
                        help='Path to the blocklist file, e.g. %s' %
                             BLOOM_DOMAIN_SOURCE)

    args = parser.parse_args(argv[1:])
    filename = os.path.abspath(args.filename)
    if not os.path.isfile(filename):
        print('File not found.')
        sys.exit(1)

    try:
        db = create_db()
        main(db, filename)
    finally:
        db.close()
