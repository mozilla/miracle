import json


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
