from datetime import datetime

from sqlalchemy import delete
from sqlalchemy import select

from miracle.models import User


def delete_data(task, user):
    # Delete user data from the database.
    exists = False
    with task.db.session() as session:
        row = session.execute(
            select([User.id, User.created]).where(User.token == user)
        ).fetchone()
        if row:
            created = row[1]
            result = session.execute(delete(User).where(User.token == user))
            exists = bool(result.rowcount)
    if exists:
        task.stats.increment('data.user.delete')
        if created:
            now = datetime.utcnow().replace(second=0, microsecond=0)
            diff_hours = int(round((now - created).total_seconds() / 3600.0))
            task.stats.timing('data.user.delete_hours', diff_hours)
    return exists


def main(task, user, _delete_data=True):
    if not user:
        return False

    # Testing hooks.
    if _delete_data is True:  # pragma: no cover
        _delete_data = delete_data
    elif not _delete_data:
        return True

    return _delete_data(task, user)
