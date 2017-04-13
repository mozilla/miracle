import time

import boto3
import botocore

from miracle.config import (
    KINESIS_ENDPOINT,
    KINESIS_FRONTEND_STREAM,
    TESTING,
)


def create_kinesis(frontend_stream=KINESIS_FRONTEND_STREAM, _kinesis=None):
    if _kinesis is not None:
        return _kinesis

    return Kinesis(frontend_stream)


class Kinesis(object):

    # Sligntly more than kinesalite's createStreamMs/deleteStreamMs
    _delay = 0.03
    client = None

    def __init__(self, frontend_stream):
        self.frontend_stream = frontend_stream
        extra_config = {}
        if TESTING:
            extra_config = {
                'endpoint_url': KINESIS_ENDPOINT,
                'region_name': 'kinesalite',
            }
        self.client = boto3.client('kinesis', **extra_config)

    def clear(self):
        if not self.client:
            return
        try:
            names = self.client.list_streams()['StreamNames']
            self._delete_streams(names)
        except botocore.exceptions.ClientError:  # pragma: no cover
            pass
        self.client.create_stream(
            StreamName=self.frontend_stream,
            ShardCount=2,
        )
        time.sleep(self._delay)
        waiter = self.client.get_waiter('stream_exists')
        waiter.wait(StreamName=self.frontend_stream)

    def close(self):
        try:
            self.client._endpoint.http_session.close()
        except AttributeError:  # pragma: no cover
            pass
        self.client = None

    def ping(self, raven):
        try:
            self.client.describe_stream(
                StreamName=self.frontend_stream, Limit=1)
        except botocore.exceptions.ClientError:  # pragma: no cover
            raven.captureException()
            return False
        return True

    def _delete_streams(self, names):
        for name in names:
            self.client.delete_stream(StreamName=name)
        if names:
            time.sleep(self._delay)
            waiter = self.client.get_waiter('stream_not_exists')
            for name in names:
                waiter.wait(StreamName=name)

    def _delete_frontend_stream(self):
        self._delete_streams([self.frontend_stream])

    def get_frontend_stream_records(self, sequence_number=None, shard_id=None):
        if shard_id:
            shard_ids = [shard_id]
        else:
            info = self.client.describe_stream(StreamName=self.frontend_stream)
            shard_ids = [shard['ShardId'] for shard in
                         info['StreamDescription']['Shards']]

        records = []
        for id_ in shard_ids:
            if sequence_number:
                iter_args = {
                    'ShardIteratorType': 'AT_SEQUENCE_NUMBER',
                    'StartingSequenceNumber': sequence_number,
                }
                limit_args = {'Limit': 1}
            else:
                iter_args = {
                    'ShardIteratorType': 'TRIM_HORIZON',
                }
                limit_args = {}

            shard_iter = self.client.get_shard_iterator(
                StreamName=self.frontend_stream,
                ShardId=id_, **iter_args)['ShardIterator']

            record_info = self.client.get_records(
                ShardIterator=shard_iter, **limit_args)
            records.extend([r['Data'] for r in record_info['Records']])

        return records
