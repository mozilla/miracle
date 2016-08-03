import sys

from miracle.config import BLOOM_DOMAIN_SOURCE
from miracle.db import create_db
from miracle.models import URL


def read_source(filename=BLOOM_DOMAIN_SOURCE, _max=None):
    lines = []
    with open(filename, 'rt', encoding='utf-8') as fd:
        i = 0
        for line in fd.readlines():
            line = line.strip()
            if line:
                lines.append(line)
                i += 1
            if _max is not None and i >= _max:
                break
    return lines


def remove_urls(db, lines):
    found_url_ids = []
    with db.session(commit=False) as session:
        # Get a list of URL ids to delete in larger batches.
        for i in range(0, len(lines), 100):
            name_batch = lines[i:i + 100]
            if name_batch:
                rows = (session.query(URL.id)
                               .filter(URL.hostname.in_(name_batch)).all())
            if rows:
                found_url_ids.extend([row[0] for row in rows])

    if not found_url_ids:
        return 0

    found_url_ids.sort()
    actually_deleted = 0
    for i in range(0, len(found_url_ids), 10):
        # Delete URLs by id in small transactional batches, as these
        # can result in large numbers of sessions to be deleted at the
        # same time.
        id_batch = found_url_ids[i:i + 10]
        if id_batch:
            with db.session() as session:
                result = (session.query(URL)
                                 .filter(URL.id.in_(id_batch))
                                 .delete(synchronize_session=False))
                actually_deleted += result

    return actually_deleted


def main(db, filename=BLOOM_DOMAIN_SOURCE):
    lines = read_source(filename)
    urls_removed = remove_urls(db, lines)
    return urls_removed


def console_entry():  # pragma: no cover
    argv = sys.argv
    try:
        db = create_db()
        main(db, argv[1])
    finally:
        db.close()
