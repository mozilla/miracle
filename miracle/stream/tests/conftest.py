import io

from amazon_kclpy.messages import (
    InitializeInput,
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
        'shardId': '0',
        'sequenceNumber': '0',
        'subSequenceNumber': 0,
        'action': 'initialize',
    })


@pytest.fixture(scope='function')
def shutdown_msg_term():
    yield ShutdownInput({
        'reason': 'TERMINATE',
        'action': 'shutdown',
    })


@pytest.fixture(scope='function')
def shutdown_msg_zombie():
    yield ShutdownInput({
        'reason': 'ZOMBIE',
        'action': 'shutdown',
    })


@pytest.fixture(scope='function')
def processor(raven, bucket, crypto, stats):
    processor = RecordProcessor(
        dummy_func,
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


def dummy_func(*args, **kw):  # pragma: no cover
    return (None, None)
