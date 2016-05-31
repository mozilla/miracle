from io import BytesIO

import boto3
import botocore
from botocore.response import StreamingBody

from contextgraph.config import (
    S3_BUCKET,
    TESTING,
)


def create_bucket(s3_bucket=S3_BUCKET, _bucket=None):
    if _bucket is not None:
        return _bucket

    klass = DebugBucket if TESTING else Bucket
    return klass(s3_bucket)


class Bucket(object):

    _bucket = None
    _resource = None

    def __init__(self, name):
        self.name = name

    def connect(self, raven):  # pragma: no cover
        self._resource = s3 = boto3.resource('s3')
        self._bucket = bucket = s3.Bucket(self.name)
        try:
            s3.meta.client.head_bucket(bucket)
        except botocore.exceptions.ClientError:
            raven.captureException()
            return False
        return True

    def delete(self, key, **kw):  # pragma: no cover
        obj = self._bucket.Object('key')
        obj.delete(**kw)

    def get(self, key, **kw):  # pragma: no cover
        obj = self._bucket.Object('key')
        return obj.get(**kw)

    def put(self, key, body,
            content_encoding=None,
            content_type='application/json', **kw):  # pragma: no cover
        obj = self._bucket.Object(key)
        obj.put(Body=body,
                ContentEncoding=content_encoding,
                ContentType=content_type,
                **kw)


class DebugBucket(Bucket):

    def __init__(self, name):
        super(DebugBucket, self).__init__(name)
        self.clear()

    def clear(self):
        self.objects = {}

    def connect(self, raven):
        return True

    def delete(self, key, **kw):
        for path in list(self.objects.keys()):
            if path.startswith(key):
                del self.objects[path]

    def get(self, key, **kw):
        obj = self.objects[key]
        res = dict(obj)
        body = res['Body']
        res['Body'] = StreamingBody(BytesIO(body), len(body))
        return res

    def put(self, key, body,
            content_encoding=None,
            content_type='application/json', **kw):
        self.objects[key] = {
            'Body': body,
            'ContentEncoding': content_encoding,
            'ContentType': content_type,
        }
