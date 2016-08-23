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


def delete_urls(task, url_ids):
    # Delete orphaned urls data from the database.
    deleted_url_count = 0
    with task.db.session() as session:
        rows = session.execute(
            select([URL.id])
            .select_from(URL.__table__.outerjoin(Session))
            .where(URL.id.in_(url_ids))
            .where(Session.url_id.is_(None))
        ).fetchall()
        orphaned_url_ids = list({row.id for row in rows})
        if orphaned_url_ids:
            result = session.execute(
                delete(URL).where(URL.id.in_(orphaned_url_ids)))
            deleted_url_count = result.rowcount
    return deleted_url_count


def delete_urls_main(task, url_ids, _delete_urls=True):
    if not url_ids:
        return False

    # Testing hooks.
    if _delete_urls is True:  # pragma: no cover
        _delete_urls = delete_urls
    elif not _delete_urls:
        return True

    return _delete_urls(task, url_ids)


def delete_user(task, user):
    # Delete user data from the database.
    exists = False
    url_ids = []
    with task.db.session() as session:
        user_row = session.execute(
            select([User.id, User.created]).where(User.token == user)
        ).fetchone()
        if user_row:
            created = user_row.created
            rows = session.execute(
                select([Session.url_id], distinct=True)
                .where(Session.user_id == user_row.id)
            ).fetchall()
            # All urls associated with the to-be-deleted user.
            url_ids = [row.url_id for row in rows]

            result = session.execute(delete(User).where(User.token == user))
            exists = bool(result.rowcount)
    if exists:
        task.stats.increment('data.user.delete')
        if created:
            now = datetime.utcnow().replace(second=0, microsecond=0)
            diff_hours = int(round((now - created).total_seconds() / 3600.0))
            task.stats.timing('data.user.delete_hours', diff_hours)
    return (exists, url_ids)


def delete_user_main(task, user, delete_urls, _delete_user=True):
    if not user:
        return False

    # Testing hooks.
    if _delete_user is True:  # pragma: no cover
        _delete_user = delete_user
    elif not _delete_user:
        return True

    user_deleted, url_ids = _delete_user(task, user)

    if url_ids:
        delete_urls.delay(url_ids)

    return user_deleted
