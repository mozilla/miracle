import time

import boto3
import botocore

from miracle.config import (
    KINESIS_ENDPOINT,
    KINESIS_STREAM,
    TESTING,
)


def create_kinesis(stream=KINESIS_STREAM, _kinesis=None):
    if _kinesis is not None:  # pragma: no cover
        return _kinesis

    return Kinesis(KINESIS_STREAM)


class Kinesis(object):

    client = None

    def __init__(self, name):
        self.name = name
        extra_config = {}
        if TESTING:
            extra_config = {
                'endpoint_url': KINESIS_ENDPOINT,
                'region_name': 'kinesalite',
            }
        self.client = boto3.client('kinesis', **extra_config)

    def clear(self):
        try:
            names = self.client.list_streams()['StreamNames']
            for name in names:
                self.client.delete_stream(StreamName=name)
            if names:
                # Sligntly more than kinesalite's deleteStreamMs
                time.sleep(0.15)
                waiter = self.client.get_waiter('stream_not_exists')
                for name in names:
                    waiter.wait(StreamName=name)
        except botocore.exceptions.ClientError:  # pragma: no cover
            pass
        self.client.create_stream(
            StreamName=self.name,
            ShardCount=2,
        )
        # Sligntly more than kinesalite's createStreamMs
        time.sleep(0.15)
        waiter = self.client.get_waiter('stream_exists')
        waiter.wait(StreamName=self.name)

    def close(self):
        try:
            self.client._endpoint.http_session.close()
        except AttributeError:  # pragma: no cover
            pass
        self.client = None

    def ping(self, raven):
        try:
            self.client.describe_stream(StreamName=self.name, Limit=1)
        except botocore.exceptions.ClientError:  # pragma: no cover
            raven.captureException()
            return False
        return True
