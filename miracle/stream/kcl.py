# This is based in large parts on the amazon_kclpy sample application:
# https://github.com/awslabs/amazon-kinesis-client-python/blob/master/samples/sample_kclpy_app.py

import time

from amazon_kclpy import kcl
from amazon_kclpy.v2 import processor

from miracle.bucket import create_bucket
from miracle.crypto import create_crypto
from miracle.log import (
    configure_logging,
    create_raven,
    create_stats,
)

CHECKPOINT_RETRIES = 4
CHECKPOINT_RETRY_WAIT = 1.5
CHECKPOINT_SECONDS = 60.0


def run_kcl_process(func, batch_size=None):  # pragma: no cover
    configure_logging()
    processor = RecordProcessor(func, batch_size=batch_size)
    kcl_process = Process(processor)
    kcl_process.run()


class Process(kcl.KCLProcess):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.raven = self.processor.raven

    def _perform_action(self, action):
        try:
            action.dispatch(self.checkpointer, self.processor)
        except Exception:
            self.raven.captureException()


class RecordProcessor(processor.RecordProcessorBase):

    def __init__(self, func, batch_size=None,
                 _bucket=None, _crypto=None, _raven=None, _stats=None):
        self.name = func.__module__ + ':' + func.__qualname__
        self.func = func.__get__(self)
        self.batch_size = batch_size if batch_size else 100
        self.last_checkpoint = None
        self.max_seq = (None, None)
        self.shard_id = None
        self.metric_tags = ['name:%s' % self.name, 'shard:%s' % self.shard_id]

        self.bucket = create_bucket(_bucket=_bucket)
        self.crypto = create_crypto(_crypto=_crypto)
        self.raven = create_raven(transport='threaded', _raven=_raven)
        self.stats = create_stats(_stats=_stats)

    def initialize(self, initialize_input):
        self.last_checkpoint = time.time()
        seq = initialize_input.sequence_number
        seq = int(seq) if seq is not None else None
        self.max_seq = (seq, initialize_input.sub_sequence_number)
        self.shard_id = initialize_input.shard_id
        self.metric_tags = ['name:%s' % self.name, 'shard:%s' % self.shard_id]
        try:
            self.bucket.ping(self.raven)
        except Exception:  # pragma: no cover
            self.raven.captureException()
            raise

    def _checkpoint(self, checkpointer, delay=CHECKPOINT_SECONDS, force=False):
        now = time.time()
        if ((now - self.last_checkpoint) < delay) and not force:
            return False

        for num in range(1, CHECKPOINT_RETRIES + 1):
            tags = self.metric_tags + ['try:%s' % num]
            try:
                with self.stats.timed('stream.checkpoint', tags=tags):
                    checkpointer.checkpoint(self.max_seq[0], self.max_seq[1])
                    self.last_checkpoint = time.time()
                return True
            except kcl.CheckpointError as exc:
                if not (exc.value == 'ThrottlingException' and
                        num < CHECKPOINT_RETRIES):
                    self.raven.captureException()
                    return False

            # Exponential backoff, at most 45 seconds in total.
            time.sleep((num ** 2) * delay)

    def _update_max_seq(self, seq, sub_seq):
        # seq can be None for a fresh shard
        seq = int(seq) if seq is not None else None
        # Coerce sub_seq to int, to avoid int/None comparisions
        sub_seq = sub_seq if sub_seq else 0
        if (self.max_seq == (None, None) or
                (seq is not None and seq > self.max_seq[0]) or
                (seq == self.max_seq[0] and sub_seq > self.max_seq[1])):
            self.max_seq = (seq, sub_seq)
            return True
        return False

    def process_records(self, process_records_input):
        try:
            records = process_records_input.records
            with self.stats.timed('stream.process', tags=self.metric_tags):
                for i in range(0, len(records), self.batch_size):
                    seq, sub_seq = self.func(records[i:i + self.batch_size])
                    self._update_max_seq(seq, sub_seq)

            self._checkpoint(process_records_input.checkpointer)
            self.stats.increment('stream.records',
                                 len(records), tags=self.metric_tags)
        except Exception:
            self.raven.captureException()

    def shutdown(self, shutdown_input):
        try:
            if shutdown_input.reason == 'TERMINATE':
                self._checkpoint(shutdown_input.checkpointer, force=True)
        except Exception:
            self.raven.captureException()
