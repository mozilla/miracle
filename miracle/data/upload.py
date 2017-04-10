import gzip
import json
import re
import uuid

from botocore.exceptions import ClientError

VALID_USER_TOKEN = re.compile(
    r'^[!()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    r'_abcdefghijklmnopqrstuvwxyz~]*$')


def validate_user(user):
    if not isinstance(user, str):
        return None
    if len(user) < 3 or len(user) > 36:
        return None
    if VALID_USER_TOKEN.match(user) is None:
        return None
    return user


def validate(data):
    if not (isinstance(data, dict) and 'user' in data):
        return None

    if not validate_user(data['user']):
        return None

    return data


def upload(task, data):
    try:
        user_token = data['user']
        blob = json.dumps(data).encode('utf-8')
        blob = gzip.compress(blob, 6)
        name = 'v2/sessions/%s/%s.json.gz' % (user_token, uuid.uuid1().hex)
        task.app.bucket.put(
            name, blob,
            ContentEncoding='gzip',
            ContentType='application/json')
    except ClientError:  # pragma: no cover
        task.app.raven.captureException()
        return False

    return True


class Upload(object):

    def __init__(self, task):
        self.task = task

    def error_stat(self, reason):
        self.task.app.stats.increment(
            'data.upload.error', tags=['reason:%s' % reason])

    def __call__(self, sequence_number=None, shard_id=None):
        records = self.task.app.kinesis.get_frontend_stream_records(
            sequence_number=sequence_number,
            shard_id=shard_id,
        )

        try:
            data = self.task.app.crypto.decrypt(records[0].decode('ascii'))
        except ValueError:
            self.error_stat('encryption')
            return False

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.error_stat('json')
            return False

        parsed_data = validate(data)
        if not parsed_data:
            self.error_stat('validation')
            return False

        success = upload(self.task, parsed_data)
        return success
