import base64
import io
import time

from amazon_kclpy.messages import (
    InitializeInput,
    ProcessRecordsInput,
    Record,
    ShutdownInput,
)
import pytest

from miracle.stream.kcl import (
    Process,
    RecordProcessor,
)


@pytest.fixture(scope='function')
def input_file():
    buf = io.StringIO()
    yield buf
    buf.close()


@pytest.fixture(scope='function')
def output_file():
    buf = io.StringIO()
    yield buf
    buf.close()


@pytest.fixture(scope='function')
def error_file():
    buf = io.StringIO()
    yield buf
    buf.close()


@pytest.fixture(scope='function')
def init_msg():
    yield InitializeInput({
        'action': 'initialize',
        'shardId': 'shard-0000',
        'sequenceNumber': '0',
        'subSequenceNumber': 0,
    })


@pytest.fixture(scope='function')
def process_msg():
    yield ProcessRecordsInput({
        'action': 'processRecords',
        'millisBehindLatest': 1,
        'records': [Record({
            'action': 'record',
            'partitionKey': 'partition-0',
            'sequenceNumber': '1',
            'subSequenceNumber': 0,
            'approximateArrivalTimestamp': time.time() * 1000.0,
            'data': base64.b64encode(b'{"user": "foo", "extra": 1}'),
        }), Record({
            'action': 'record',
            'partitionKey': 'partition-1',
            'sequenceNumber': '2',
            'subSequenceNumber': 0,
            'approximateArrivalTimestamp': time.time() * 1000.0,
            'data': base64.b64encode(b'{"user": "bar", "extra": 2}'),
        })],
    })


@pytest.fixture(scope='function')
def shutdown_msg_term():
    yield ShutdownInput({
        'action': 'shutdown',
        'reason': 'TERMINATE',
    })


@pytest.fixture(scope='function')
def shutdown_msg_zombie():
    yield ShutdownInput({
        'action': 'shutdown',
        'reason': 'ZOMBIE',
    })


@pytest.fixture(scope='function')
def processor(raven, bucket, crypto, stats):
    processor = RecordProcessor(
        func,
        _raven=raven,
        _bucket=bucket,
        _crypto=crypto,
        _stats=stats)
    yield processor


@pytest.fixture(scope='function')
def process(processor, input_file, output_file, error_file, init_msg):
    proc = Process(processor, input_file=input_file,
                   output_file=output_file, error_file=error_file)
    proc._perform_action(init_msg)
    yield proc


def func(processor, records):
    return max([(r.sequence_number, r.sub_sequence_number) for r in records])
