from datetime import datetime
from ipaddress import ip_address
import json
import time
from urllib.parse import urlsplit

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
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
    # Ensure that each field is of the expected type and
    # inside the expected min/max range.
    if not isinstance(value, type_):
        return None

    if (type_ in (int, float) and
            not (min_value <= value < max_value)):
        value = None
    elif (type_ is str and
          not (min_value <= len(value) < max_value)):
        value = None

    return value


def validate(data, bloom_domain):
    # Validate the incoming data against the schema and filter out
    # any unwanted sessions.
    if (not isinstance(data, dict) or
            'sessions' not in data or
            not isinstance(data['sessions'], list)):
        return ({'sessions': []}, 0, 0)

    drop_urls = set()
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
            filtered_entry = filter_entry(validated_entry, bloom_domain)
            if filtered_entry:
                sessions.append(filtered_entry)
            else:
                drop_urls.add(validated_entry['url'])

    # Return filtered session data, the number of dropped URLs and
    # the number of dropped sessions.
    return ({'sessions': sessions},
            len(drop_urls),
            len(data['sessions']) - len(sessions))


def filter_entry(session_entry, bloom_domain):
    # Check each session entry and filter some of them out.
    url_result = urlsplit(session_entry['url'])
    if (url_result.username or url_result.password or
            url_result.scheme not in ('http', 'https')):
        return None

    if url_result.hostname in bloom_domain:
        # Filter out domains based on a blocklist.
        return None

    # Filter out private IP addresses.
    try:
        ip = ip_address(url_result.hostname)
    except ValueError:
        pass
    else:
        if not ip.is_global:
            return None

    return session_entry


def _create_urls(session, new_urls):
    # Get or create URLs
    added_urls = 0
    url_values = []

    urls = dict(session.execute(
        select([URL.url, URL.id]).where(URL.url.in_(new_urls))).fetchall())

    for new_url in new_urls:
        if new_url not in urls:
            added_urls += 1
            urls[new_url] = None
            url_values.append(URL.from_url(new_url))

    if url_values:
        stmt = insert(URL).on_conflict_do_nothing()
        session.execute(stmt, url_values)

    return (added_urls, urls)


def _create_user(session, user_token):
    # Get or create user
    added_user = 0
    user_id = None

    row = session.execute(
        select([User.id]).where(User.token == user_token)).fetchone()
    if row:
        user_id = row[0]
    else:
        added_user = 1
        stmt = (insert(User)
                .on_conflict_do_nothing()
                .values(token=user_token))
        result = session.execute(stmt)
        user_id = result.inserted_primary_key[0]

    return (added_user, user_id)


def _upload_data(task, user_token, data, _lock_timeout=10000):
    # Insert data into the database.
    new_urls = {sess['url'] for sess in data['sessions']}

    with task.db.session() as session:
        # First do UPSERTs for new URLs and the user in its own transaction.
        # This lets the DB do conflict resolution via
        # "insert on conflict do nothing".
        session.execute('SET LOCAL lock_timeout = %s' % _lock_timeout)
        added_urls, urls = _create_urls(session, new_urls)
        added_user, user_id = _create_user(session, user_token)

    # Determine newly created URLs without an id.
    missing_url_ids = {url for url, url_id in urls.items() if url_id is None}

    with task.db.session() as session:
        # In the second transaction add sessions and find all
        # newly created URL ids.

        if missing_url_ids:
            # Get missing URL ids.
            found_urls = dict(session.execute(
                select([URL.url, URL.id]).where(
                    URL.url.in_(missing_url_ids))).fetchall())

            urls.update(found_urls)

        session_values = []
        for entry in data['sessions']:
            session_values.append({
                'user_id': user_id,
                'url_id': urls[entry['url']],
                'duration': entry['duration'],
                'start_time': datetime.utcfromtimestamp(entry['start_time']),
            })

        if session_values:
            # Bulk insert new sessions.
            session.execute(insert(Session), session_values)

    # Emit metrics outside of the db transaction scope.
    task.stats.increment('data.url.new', added_urls)
    task.stats.increment('data.user.new', added_user)
    task.stats.increment('data.session.new', len(data['sessions']))
    return True


def upload_data(task, user_token, data,
                _lock_timeout=10000, _retries=3, _retry_wait=1.0):
    # Upload data wrapper, to retry upload on database errors.
    success = False
    for i in range(_retries):
        try:
            success = _upload_data(task, user_token, data,
                                   _lock_timeout=_lock_timeout)
        except OperationalError:
            time.sleep(_retry_wait * (i ** 2 + 1))

        if success:
            break

    return success


def main(task, user, payload, _upload_data=True):
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        task.stats.increment('data.upload.error.json')
        return False

    parsed_data, drop_urls, drop_sessions = validate(data, task.bloom_domain)
    task.stats.increment('data.url.drop', drop_urls)
    task.stats.increment('data.session.drop', drop_sessions)
    if not parsed_data['sessions']:
        task.stats.increment('data.upload.error.validation')
        return False

    # Testing hooks
    if _upload_data is True:  # pragma: no cover
        _upload_data = upload_data
    elif not _upload_data:
        return True

    success = _upload_data(task, user, parsed_data)
    if not success:  # pragma: no cover
        task.stats.increment('data.upload.error.db')
    return success
