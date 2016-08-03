from miracle.config import BLOOM_DOMAIN_SOURCE
from miracle.db import create_db
from miracle.models import URL


def read_source():
    lines = []
    with open(BLOOM_DOMAIN_SOURCE, 'rt', encoding='utf-8') as fd:
        for line in fd.readlines:
            line = line.strip()
            if line:
                lines.append(line)
    return lines


def main(db):
    lines = read_source()

    found_url_ids = []
    with db.session() as session:
        for i in range(0, len(lines), 100):
            rows = (session.query(URL.id)
                           .filter(URL.hostname.in_(lines[i:i + 100])).all())
            import pdb; pdb.set_trace()


def console_entry():  # pragma: no cover
    try:
        db = create_db()
        main(db)
    finally:
        db.close()
