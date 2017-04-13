#!/usr/bin/env python

import sys

from miracle.config import (
    DYNAMODB_ENDPOINT,
    KINESIS_ENDPOINT,
    KINESIS_FRONTEND_STREAM,
)
from miracle import stream

CONFIGFILE = 'kcl-frontend-s3.properties'
PYTHON_VERSION = '.'.join([str(i) for i in sys.version_info[:3]])
STREAM_BASE_PATH = stream.__path__[0]

# Must be at least 200 ms if a single consumer reads from a stream,
# otherwise at least 200 ms multiplied by the number of consumer.
# See http://docs.aws.amazon.com/streams/latest/dev/kinesis-low-latency.html
IDLE_TIME = 250

# Use TRIM_HORIZON to process messages which had been added to the stream
# before any consumers were started and thus no DynamoDB tracking data
# was available.
# http://docs.aws.amazon.com/streams/latest/dev/kinesis-record-processor-additional-considerations.html
INITIAL_POSITION = 'TRIM_HORIZON'

TEMPLATE = '''\
AWSCredentialsProvider = DefaultAWSCredentialsProviderChain
processingLanguage = python/{pythonVersion}
initialPositionInStream = {initialPosition}

failoverTimeMillis = 30000
idleTimeBetweenReadsInMillis = {idleTime}

executableName = python -u {basePath}/frontend_s3.py
applicationName = miracle-frontend-s3
streamName {streamName}

'''


def main():
    data = TEMPLATE.format(
        basePath=STREAM_BASE_PATH,
        idleTime=IDLE_TIME,
        initialPosition=INITIAL_POSITION,
        pythonVersion=PYTHON_VERSION,
        streamName=KINESIS_FRONTEND_STREAM,
    )
    if DYNAMODB_ENDPOINT:
        data += 'dynamoDBEndpoint = %s\n' % DYNAMODB_ENDPOINT
    if KINESIS_ENDPOINT:
        data += 'kinesisEndpoint = %s\n' % KINESIS_ENDPOINT

    with open(CONFIGFILE, 'w') as fd:
        fd.write(data)


if __name__ == '__main__':
    main()
