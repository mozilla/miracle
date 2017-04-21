from datetime import date
import gzip
import json
import re
import uuid

from botocore.exceptions import ClientError

from miracle.stream.kcl import run_kcl_process


VALID_USER_TOKEN = re.compile(
    r'^[!()*-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    r'_abcdefghijklmnopqrstuvwxyz~]*$')


def error_stat(stats, reason):
    stats.increment('stream.process.error', tags=['reason:%s' % reason])


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


def upload(processor, data):
    user_token = data['user']
    today = date.today()
    blob = json.dumps(data, separators=(',', ':')).encode('utf-8')
    blob = gzip.compress(blob, 7)
    name = 'v2/sessions/%s/%s/%s/%s.json.gz' % (
        today.year, today.month, user_token, uuid.uuid1().hex)
    try:
        processor.bucket.put(
            name, blob,
            ContentEncoding='gzip',
            ContentType='application/json')
    except ClientError:  # pragma: no cover
        processor.raven.captureException()
        return False

    return True


def main(processor, records):
    seq = None
    sub_seq = None
    for record in records:
        try:
            data = processor.crypto.decrypt(record.binary_data.decode('ascii'))
        except ValueError:
            error_stat(processor.stats, 'encryption')
            continue

        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            error_stat(processor.stats, 'json')
            continue

        parsed_data = validate(data)
        if not parsed_data:
            error_stat(processor.stats, 'validation')
            continue

        success = upload(processor, parsed_data)
        if success:
            seq = record.sequence_number
            sub_seq = record.sub_sequence_number

    return (seq, sub_seq)


if __name__ == "__main__":  # pragma: no cover
    run_kcl_process(main, batch_size=10)
