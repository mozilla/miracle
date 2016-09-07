import argparse
from collections import defaultdict
import sys

from sqlalchemy import (
    cast,
    extract,
    func,
    Integer,
    select,
)

from miracle.db import create_db
from miracle.log import (
    configure_logging,
    LOGGER,
)
from miracle.models import Session

ONE_WEEK_SEC = 7 * 24 * 3600


def user_weekly_recurrence(session, user_id, min_count=3):
    # Get all URLs which have been visited at least 3 times overall.
    rows = session.execute(
        select([Session.url_id])
        .where(Session.user_id == user_id)
        .group_by(Session.url_id)
        .having(func.count() >= min_count)
    ).fetchall()

    url_ids = [row.url_id for row in rows]
    if not url_ids:
        return 0

    # Get all session times for URLs with more than three visits.
    rows = session.execute(
        select([Session.url_id,
                cast(extract('epoch', Session.start_time),
                     Integer).label('start')])
        .where(Session.user_id == user_id)
        .where(Session.url_id.in_(url_ids))
    ).fetchall()

    # Group by URL.
    url_times = defaultdict(list)
    for row in rows:
        url_times[row.url_id].append(row.start)

    found = 0
    for url_id, times in url_times.items():
        times = sorted(times)
        for i in range(0, len(times) - min_count + 1):
            # We don't need to look at the last elements, as there
            # are too few sessions to compare to.
            first = times.pop(0)
            if times[min_count - 2] - first <= ONE_WEEK_SEC:
                # Since the first element is popped from the list,
                # with min_count=2, we'd have to compare to the
                # new first element at position 0, so we subtract
                # one for zero based indexing and one to account for
                # the pop.
                found += 1
                break

    return found


def weekly_recurrence(db):
    user_results = {}

    with db.session(commit=False) as session:
        user_rows = session.execute(
            select([Session.user_id], distinct=True)).fetchall()
        user_ids = [u.user_id for u in user_rows]

        for user_id in user_ids:
            user_results[user_id] = user_weekly_recurrence(session, user_id)

    num_users = defaultdict(int)
    for num in user_results.values():
        num_users[num] += 1

    return sorted([(k, v) for k, v in num_users.items()])


def main(db, mode):
    LOGGER.info('Starting analysis: %s', mode)
    LOGGER.info('Number of recurring URLs per 7 days to user count:')
    LOGGER.info(weekly_recurrence(db))
    LOGGER.info('Finished analysis.')
    return True


def console_entry():  # pragma: no cover
    configure_logging()
    argv = sys.argv

    parser = argparse.ArgumentParser(
        prog=argv[0],
        description='Count')
    parser.add_argument('--mode', required=True,
                        help='Type of analysis, one of: weekly_recurrence')

    args = parser.parse_args(argv[1:])
    if args.mode not in ('weekly_recurrence', ):
        print('Unknown analysis mode.')
        sys.exit(1)

    result = True
    try:
        db = create_db()
        result = main(db, args.mode)
    finally:
        db.close()
    sys.exit(int(not result))
