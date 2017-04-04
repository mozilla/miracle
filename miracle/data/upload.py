from functools import lru_cache
import gzip
from ipaddress import _BaseAddress
import json
import re
import socket
import time
import uuid

from botocore.exceptions import ClientError
from uritools import urisplit

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


def validate(data):
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
            filtered_entry = filter_entry(validated_entry)
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


def filter_entry(session_entry):
    # Check each session entry and filter some of them out.
    try:
        url_result = urisplit(session_entry['url'])
        host = url_result.gethost()
    except ValueError:  # pragma: no cover
        return None

    if (url_result.scheme not in ('http', 'https') or url_result.userinfo):
        return None

    if isinstance(host, str):
        # Filter out localhost, .local
        if host == 'localhost' or host.endswith('.local'):
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


def upload_data(task, data):
    try:
        user_token = data['user']
        blob = json.dumps(data).encode('utf-8')
        blob = gzip.compress(blob, 6)
        name = 'v2/sessions/%s/%s.json.gz' % (user_token, uuid.uuid1().hex)
        task.bucket.put(
            name, blob,
            ContentEncoding='gzip',
            ContentType='application/json')
    except ClientError:  # pragma: no cover
        task.raven.captureException()
        return False

    task.stats.increment('data.session.new', len(data['sessions']))
    return True


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

        parsed_data, drop_urls, drop_sessions = validate(data)

        self.task.stats.increment('data.url.drop', drop_urls)
        self.task.stats.increment('data.session.drop', drop_sessions)

        if not parsed_data:
            self.error_stat('validation')
            return False

        success = upload_data(self.task, parsed_data)
        return success
