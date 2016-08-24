from datetime import datetime

from sqlalchemy import (
    delete,
    select,
)

from miracle.models import (
    Session,
    URL,
    User,
)


class DeleteUrls(object):

    def __init__(self, task):
        self.task = task

    def __call__(self, url_ids):
        # Delete orphaned URLs data from the database.
        if not url_ids:
            return None

        deleted_url_count = 0
        with self.task.db.session() as session:
            rows = session.execute(
                select([Session.url_id], distinct=True)
                .where(Session.url_id.in_(url_ids))
            ).fetchall()
            found_url_ids = {row.url_id for row in rows}
            orphaned_url_ids = list(set(url_ids) - found_url_ids)
            if orphaned_url_ids:
                result = session.execute(
                    delete(URL).where(URL.id.in_(orphaned_url_ids)))
                deleted_url_count = result.rowcount
        return deleted_url_count


class DeleteUser(object):

    def __init__(self, task):
        self.task = task

    def delete_user(self, user):
        # Delete user data from the database.
        exists = False
        url_ids = []
        with self.task.db.session() as session:
            user_row = session.execute(
                select([User.id, User.created]).where(User.token == user)
            ).fetchone()
            if user_row:
                created = user_row.created
                rows = session.execute(
                    select([Session.url_id], distinct=True)
                    .where(Session.user_id == user_row.id)
                ).fetchall()
                # All URLs associated with the to-be-deleted user.
                url_ids = [row.url_id for row in rows]

                result = session.execute(
                    delete(User).where(User.token == user))
                exists = bool(result.rowcount)
        if exists:
            self.task.stats.increment('data.user.delete')
            if created:
                now = datetime.utcnow().replace(second=0, microsecond=0)
                diff_hours = int(round(
                    (now - created).total_seconds() / 3600.0))
                self.task.stats.timing('data.user.delete_hours', diff_hours)
        return (exists, url_ids)

    def __call__(self, user, delete_urls):
        if not user:
            return None

        user_deleted, url_ids = self.delete_user(user)
        if url_ids:
            delete_urls.delay(url_ids)

        return user_deleted
