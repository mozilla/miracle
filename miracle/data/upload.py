from datetime import datetime
import json
import time
from urllib.parse import urlsplit

from sqlalchemy.exc import OperationalError

from miracle.models import (
    URL,
    User,
    Session,
)

HISTORY_SCHEMA = [
    # (field name, field type, required, min_value, max_value)
    ('url', str, True, 0, 2048),
    ('start_time', int, True, 2 ** 29, 2 ** 32),  # year 1987-2106
    ('duration', int, False, 0, 1000 * 3600 * 24),  # max 1 day in ms
]


def check_field(value, type_, min_value, max_value):
    if not isinstance(value, type_):
        return None

    if (type_ in (int, float) and
            not (min_value <= value < max_value)):
        value = None
    elif (type_ is str and
          not (min_value <= len(value) < max_value)):
        value = None

    return value


def validate(data):
    if (not isinstance(data, dict) or
            'sessions' not in data or
            not isinstance(data['sessions'], list)):
        return

    sessions = []
    for entry in data['sessions']:
        if not isinstance(entry, dict):
            continue

        missing_field = False
        validated_entry = {}
        for field, type_, required, min_value, max_value in HISTORY_SCHEMA:
            value = check_field(entry.get(field), type_, min_value, max_value)

            if required and not value:
                missing_field = True
                break

            validated_entry[field] = value

        if not missing_field:
            filtered_entry = filter_entry(validated_entry)
            if filtered_entry:
                sessions.append(filtered_entry)

    output = {}
    if sessions:
        output['sessions'] = sessions

    return output


def filter_entry(entry):
    url_result = urlsplit(entry['url'])
    if url_result.username or url_result.password:
        return None

    return entry


def _upload_data(task, user_token, data, new_urls, _lock_timeout=10000):
    with task.db.session() as session:
        # Avoid waiting forever
        session.execute('SET LOCAL lock_timeout = %s' % _lock_timeout)
        # Check for existing user
        user = session.query(User).filter(User.token == user_token).first()
        if user is None:
            user = User(token=user_token)
            session.add(user)

        # Get already known URLs
        found_urls = (session.query(URL)
                             .filter(URL.full.in_(new_urls)).all())
        urls = {url.full: url for url in found_urls}

        for entry in data['sessions']:
            url = urls.get(entry['url'])
            if not url:
                url = URL.from_url(entry['url'])
                urls[url.full] = url
                session.add(url)

            session.add(Session(
                user_id=user.id,
                url=url,
                duration=entry['duration'],
                start_time=datetime.utcfromtimestamp(entry['start_time']),
            ))

    return True


def upload_data(task, user_token, data,
                _lock_timeout=10000, _retries=3, _retry_wait=1.0):
    new_urls = {sess['url'] for sess in data['sessions']}
    success = False
    # Retry upload on SQL unique constraint conflict error
    for i in range(_retries):
        try:
            success = _upload_data(task, user_token, data, new_urls,
                                   _lock_timeout=_lock_timeout)
        except OperationalError as exc:
            time.sleep(_retry_wait * (i ** 2 + 1))

        if success:
            break

    return success


def main(task, user, payload, _upload_data=True):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return False

    parsed_data = validate(data)
    if not parsed_data:
        return False

    # Testing hooks.
    if not _upload_data:
        return True

    if _upload_data is True:  # pragma: no cover
        _upload_data = upload_data

    return _upload_data(task, user, parsed_data)
