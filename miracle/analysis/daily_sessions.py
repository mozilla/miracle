"""
A script to measure the number of sessions a single user typically has
on any given day.

The script excludes days, where a user has had no sessions at all.
"""

from statistics import mean, median

from sqlalchemy import text

from miracle.log import LOGGER


stmt = '''\
SELECT user_id, DATE(start_time) AS day, count(*) AS num
FROM sessions GROUP BY user_id, DATE(start_time)
'''


def daily_sessions(db):
    stats = ('max: 0', 'mean: 0', 'median: 0', 'min: 0')

    with db.session(commit=False) as session:
        rows = session.execute(text(stmt)).fetchall()

    sessions = []
    for row in rows:
        sessions.append(row.num)

    if sessions:
        stats = ('max: %s' % round(max(sessions)),
                 'mean: %s' % round(mean(sessions)),
                 'median: %s' % round(median(sessions)),
                 'min: %s' % round(min(sessions)),
                 )
    return stats


def main(db, argv=None):
    result = daily_sessions(db)
    LOGGER.info('Daily sessions per user, excluding days without sessions:')
    LOGGER.info(result)
