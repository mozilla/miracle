import mock
import json

from amazon_kclpy.kcl import CheckpointError

from miracle.stream.kcl import CHECKPOINT_RETRIES


def test_init(process):
    assert hasattr(process, 'io_handler')
    assert hasattr(process, 'checkpointer')
    assert hasattr(process, 'processor')
    assert hasattr(process, 'raven')
    processor = process.processor
    assert hasattr(processor, 'bucket')
    assert hasattr(processor, 'crypto')
    assert hasattr(processor, 'raven')
    assert hasattr(processor, 'stats')
    assert processor.batch_size == 100
    assert processor.last_checkpoint is not None
    assert processor.max_seq == (None, None)
    assert processor.func.__self__ is processor


def test_perform_action(process, raven):
    process._perform_action(None)
    raven.check(['AttributeError'])


def test_shutdown_term(process, shutdown_msg_term):
    # Prepare dummy checkpoint response
    input_file = process.checkpointer.io_handler.input_file
    position = input_file.tell()
    input_file.write(json.dumps({
        'action': 'checkpoint',
        'sequenceNumber': '0',
        'subSequenceNumber': 0,
    }) + '\n')
    input_file.seek(position)

    first_checkpoint = process.processor.last_checkpoint
    process._perform_action(shutdown_msg_term)
    assert process.processor.last_checkpoint > first_checkpoint


def test_shutdown_term_fail(process, raven, shutdown_msg_term):
    shutdown_msg_term.dispatch(None, process.processor)
    raven.check(['AttributeError'])


def test_shutdown_zombie(process, shutdown_msg_zombie):
    first_checkpoint = process.processor.last_checkpoint
    process._perform_action(shutdown_msg_zombie)
    assert process.processor.last_checkpoint == first_checkpoint


def test_checkpoint_delay(process):
    checkpointer = process.checkpointer
    assert not process.processor._checkpoint(checkpointer)


def test_checkpoint_fail(process, raven):
    checkpointer = process.checkpointer

    def mock_checkpoint(self, sequence_number=None, sub_sequence_number=None):
        raise CheckpointError('InvalidStateException')

    with mock.patch.object(checkpointer, 'checkpoint', mock_checkpoint):
        assert not process.processor._checkpoint(
            checkpointer, delay=0.0001, force=True)
    raven.check(['CheckpointError'])


def test_checkpoint_throttling(process):
    checkpointer = process.checkpointer
    num = [0]

    def mock_checkpoint(self, sequence_number=None,
                        sub_sequence_number=None, num=num):
        num[0] += 1
        if num[0] == 2:
            return
        raise CheckpointError('ThrottlingException')

    with mock.patch.object(checkpointer, 'checkpoint', mock_checkpoint):
        assert process.processor._checkpoint(
            checkpointer, delay=0.0001, force=True)


def test_checkpoint_throttling_fail(process, raven):
    checkpointer = process.checkpointer
    num = [0]

    def mock_checkpoint(self, sequence_number=None,
                        sub_sequence_number=None, num=num):
        num[0] += 1
        if num[0] == CHECKPOINT_RETRIES + 2:  # pragma: no cover
            # Safety guard to not sleep forever
            return
        raise CheckpointError('ThrottlingException')

    with mock.patch.object(checkpointer, 'checkpoint', mock_checkpoint):
        assert not process.processor._checkpoint(
            checkpointer, delay=0.0001, force=True)
    raven.check(['CheckpointError'])


def test_update_max_seq(process):
    proc = process.processor
    proc._update_max_seq('10', 0)
    assert proc.max_seq == (10, 0)
    proc._update_max_seq('10', 1)
    assert proc.max_seq == (10, 1)
    proc._update_max_seq('11', 5)
    assert proc.max_seq == (11, 5)
    proc._update_max_seq('9', 7)
    assert proc.max_seq == (11, 5)
    proc._update_max_seq('11', 3)
    assert proc.max_seq == (11, 5)
    proc._update_max_seq(None, None)
    assert proc.max_seq == (11, 5)
    proc._update_max_seq(None, 0)
    assert proc.max_seq == (11, 5)
