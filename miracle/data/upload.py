from datetime import datetime
from functools import lru_cache
from ipaddress import _BaseAddress
import json
import re
import sys
import socket
import time

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError
from uritools import urisplit

from miracle.models import (
    URL,
    User,
    Session,
)

MAX_DURATION = 1000 * 3600 * 24 * 21  # max 21 days in ms
SESSION_SCHEMA = [
    # (name, type, required, min_value, max_value, underflow, overflow)
    ('url', str, True, 8, 2048, None, None),
    ('start_time', int, True, 2 ** 29, 2 ** 32, None, None),  # year 1987-2106
    ('duration', int, False, 0, MAX_DURATION, 0, MAX_DURATION),
    ('tab_id', str, False, 2, 36, '', ''),
]
VALID_USER_TOKEN = re.compile(
    r'^[!()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    r'_abcdefghijklmnopqrstuvwxyz~]*$')


def check_field(value, type_, min_value, max_value, underflow, overflow):
    # Ensure that each field is of the expected type and
    # inside the expected min/max range.
    if not isinstance(value, type_):
        return None

    range_condition = value
    if type_ is str:
        range_condition = len(value)

    if range_condition <= min_value:
        return underflow

    if range_condition > max_value:
        return overflow

    return value


def validate_user(user):
    if not isinstance(user, str):
        return None
    if len(user) < 3 or len(user) > 36:
        return None
    if VALID_USER_TOKEN.match(user) is None:
        return None
    return user


def validate(data, bloom_domain):
    # Validate the incoming data against the schema and filter out
    # any unwanted sessions.
    if (not isinstance(data, dict) or
            'sessions' not in data or
            not isinstance(data['sessions'], list) or
            'user' not in data):
        return (None, 0, 0)

    user = validate_user(data['user'])
    if not user:
        return (None, 0, 0)

    drop_urls = set()
    sessions = []
    for entry in data['sessions']:
        if not isinstance(entry, dict):
            continue

        missing_field = False
        validated_entry = {}
        for field, type_, required, *spec in SESSION_SCHEMA:
            value = check_field(entry.get(field), type_, *spec)

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

    result = None
    if sessions:
        result = {'sessions': sessions, 'user': user}

    # Return filtered session data, the number of dropped URLs and
    # the number of dropped sessions.
    return (result,
            len(drop_urls),
            len(data['sessions']) - len(sessions))


@lru_cache(maxsize=1024)
def validate_hostname(hostname):
    # Validate DNS resolution.
    try:
        socket.gethostbyname(hostname)
    except (socket.gaierror, UnicodeError):
        return False
    return True


def validate_start_time(start_time):
    # Filter out entries in the future or those more than 2 weeks old.
    now = int(time.time())
    if (start_time > now + 86400) or (start_time < now - 86400 * 14):
        return False
    return True


def filter_entry(session_entry, bloom_domain):
    # Check each session entry and filter some of them out.
    try:
        url_result = urisplit(session_entry['url'])
        host = url_result.gethost()
    except ValueError:  # pragma: no cover
        return None

    if (url_result.scheme not in ('http', 'https') or url_result.userinfo):
        return None

    if isinstance(host, str):
        if host in bloom_domain:
            # Filter out domains based on a blocklist.
            return None
    elif isinstance(host, _BaseAddress):
        # Filter out IP addresses.
        return None
    else:  # pragma: no cover
        return None

    port = url_result.getport()
    if port is not None and port not in (80, 443):
        # Filter out non-standard ports.
        return None

    if not validate_start_time(session_entry['start_time']):
        # Filter out too old or too new times.
        return None

    if not validate_hostname(host):
        # Filter out invalid or publicly unreachable hosts.
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
    now = datetime.utcnow().replace(second=0, microsecond=0)
    user_id = None

    row = session.execute(
        select([User.id]).where(User.token == user_token)).fetchone()
    if row:
        user_id = row[0]
    else:
        added_user = 1
        stmt = (insert(User)
                .on_conflict_do_nothing()
                .values(token=user_token, created=now))
        result = session.execute(stmt)
        user_id = result.inserted_primary_key[0]

    return (added_user, user_id)


def _upload_data(task, data, _lock_timeout=10000):
    # Insert data into the database.
    new_urls = {sess['url'] for sess in data['sessions']}
    user_token = data['user']

    with task.db.session() as session:
        # First do UPSERTs for new URLs and the user in its own transaction.
        # This lets the DB do conflict resolution via
        # "insert on conflict do nothing".
        stmt = text('SET LOCAL lock_timeout = :lock_timeout')
        session.execute(stmt.bindparams(lock_timeout=_lock_timeout))
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
                'tab_id': entry['tab_id'],
            })

        if session_values:
            # Bulk insert new sessions.
            session.execute(insert(Session), session_values)

    # Emit metrics outside of the db transaction scope.
    task.stats.increment('data.url.new', added_urls)
    task.stats.increment('data.user.new', added_user)
    task.stats.increment('data.session.new', len(data['sessions']))
    return True


def upload_data(task, data,
                _lock_timeout=10000, _retries=3, _retry_wait=1.0):
    # Upload data wrapper, to retry upload on database errors.
    exc_info = None
    success = False
    for i in range(max(_retries, 1)):
        try:
            success = _upload_data(task, data, _lock_timeout=_lock_timeout)
        except OperationalError:
            exc_info = sys.exc_info()
            time.sleep(_retry_wait * (i ** 2 + 1))

        if success:
            break

    if not success:
        task.raven.captureException(exc_info=exc_info)

    del exc_info
    return success


class Upload(object):

    def __init__(self, task):
        self.task = task

    def error_stat(self, reason):
        self.task.stats.increment(
            'data.upload.error', tags=['reason:%s' % reason])

    def __call__(self, payload):
        try:
            data = self.task.crypto.decrypt(payload)
        except ValueError:
            self.error_stat('encryption')
            return False

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.error_stat('json')
            return False

        parsed_data, drop_urls, drop_sessions = validate(
            data, self.task.bloom_domain)

        self.task.stats.increment('data.url.drop', drop_urls)
        self.task.stats.increment('data.session.drop', drop_sessions)

        if not parsed_data:
            self.error_stat('validation')
            return False

        success = upload_data(self.task, parsed_data)
        return success
