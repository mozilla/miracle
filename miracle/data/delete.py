from miracle.models import User


def delete_data(task, user):
    # Delete user data from the database.
    exists = False
    with task.db.session() as session:
        exists = bool(session.query(User).filter(User.token == user).delete())
    if exists:
        task.stats.increment('data.user.delete')
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
