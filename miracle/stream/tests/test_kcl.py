import io
import json
import time

from amazon_kclpy.kcl import (
    _IOHandler,
    Checkpointer,
)
from amazon_kclpy.messages import (
    InitializeInput,
    ShutdownInput,
)
import pytest

from miracle.stream.kcl import RecordProcessor


@pytest.fixture(scope='function')
def io_handler():
    yield _IOHandler(input_file=io.StringIO(), output_file=io.StringIO(),
                     error_file=io.StringIO())


@pytest.fixture(scope='function')
def checkpointer(io_handler):
    yield Checkpointer(io_handler)


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


def dummy_func(*args, **kw):  # pragma: no cover
    return (None, None)


def test_batch_size():
    proc = RecordProcessor(dummy_func, batch_size=20)
    assert proc.batch_size == 20


def test_init(checkpointer, init_msg):
    now = time.time()
    proc = RecordProcessor(dummy_func)
    init_msg.dispatch(checkpointer, proc)

    assert proc.batch_size == 100
    assert proc.last_checkpoint > now
    assert proc.max_seq == (None, None)
    assert proc.func.__self__ is proc


def test_shutdown_term(checkpointer, init_msg, shutdown_msg_term):
    now = time.time()
    proc = RecordProcessor(dummy_func)
    init_msg.dispatch(checkpointer, proc)
    first_checkpoint = proc.last_checkpoint
    assert first_checkpoint > now

    # Prepare dummy checkpoint response
    checkpointer.io_handler.input_file.write(json.dumps({
        'action': 'checkpoint',
        'sequenceNumber': '0',
        'subSequenceNumber': 0,
    }) + '\n')
    checkpointer.io_handler.input_file.seek(0)

    shutdown_msg_term.dispatch(checkpointer, proc)
    assert proc.last_checkpoint > first_checkpoint


def test_shutdown_zombie(checkpointer, init_msg, shutdown_msg_zombie):
    now = time.time()
    proc = RecordProcessor(dummy_func)
    init_msg.dispatch(checkpointer, proc)
    first_checkpoint = proc.last_checkpoint
    assert first_checkpoint > now

    shutdown_msg_zombie.dispatch(checkpointer, proc)
    assert proc.last_checkpoint == first_checkpoint


def test_shutdown_fail(checkpointer, init_msg, shutdown_msg_zombie):
    proc = RecordProcessor(dummy_func)
    init_msg.dispatch(checkpointer, proc)
    shutdown_msg_zombie.dispatch(None, proc)
