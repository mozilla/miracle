# This is based in large parts on the amazon_kclpy sample application:
# https://github.com/awslabs/amazon-kinesis-client-python/blob/master/samples/sample_kclpy_app.py

import sys
import time

from amazon_kclpy import kcl
from amazon_kclpy.v2 import processor


CHECKPOINT_RETRIES = 4
CHECKPOINT_RETRY_WAIT = 1.5
CHECKPOINT_SECONDS = 60.0


def run_kcl_process(processor):
    kcl_process = kcl.KCLProcess(processor)
    kcl_process.run()


class BaseRecordProcessor(processor.RecordProcessorBase):

    def __init__(self):
        self.last_checkpoint = None
        self.max_seq = (None, None)

    def initialize(self, initialize_input):
        self.last_checkpoint = time.time()

    def _log(self, message):
        sys.stderr.write(message + '\n')

    def _wait(self, num):
        # Exponential backoff, at most 45 seconds in total.
        time.sleep((num ** 2) * CHECKPOINT_SECONDS)

    def _checkpoint(self, checkpointer, force=False):
        now = time.time()
        if ((now - self.last_checkpoint) < CHECKPOINT_SECONDS) and not force:
            return False

        for num in range(1, CHECKPOINT_RETRIES + 1):
            try:
                checkpointer.checkpoint(self.max_seq[0], self.max_seq[1])
                return True
            except kcl.CheckpointError as exc:
                if exc.value == 'ShutdownException':
                    self._log(
                        'Encountered shutdown exception, skipping checkpoint')
                    return False
                elif exc.value == 'ThrottlingException':
                    if num > CHECKPOINT_RETRIES:
                        self._log('Failed to checkpoint '
                                  'after %s attempts.' % num)
                        return False
                    else:
                        # TODO This is the only non-return case.
                        self._log('Was throttled while checkpointing')
                elif exc.value == 'InvalidStateException':
                    self._log('MultiLangDaemon reported an invalid state '
                              'while checkpointing.')
                    return False
                else:
                    self._log('Encountered an error while checkpointing, '
                              'error was %r.' % exc)
                    return False
            self._wait(num)

        return None

    def _update_max_seq(self, seq, sub_seq):
        seq = int(seq) if seq is not None else None
        if (self.max_seq == (None, None) or
                seq > self.max_seq[0] or
                (seq == self.max_seq[0] and sub_seq > self.max_seq[1])):
            self.max_seq = (seq, sub_seq)
            return True
        return False

    def _process_record(self, data, key, seq, sub_seq):
        raise NotImplementedError()

    def process_records(self, process_records_input):
        seq = None
        sub_seq = None
        try:
            for record in process_records_input.records:
                data = record.binary_data
                key = record.partition_key
                seq = record.sequence_number
                sub_seq = record.sub_sequence_number
                self._process_record(data, key, seq, sub_seq)
                self._update_max_seq(seq, sub_seq)
            self._checkpoint(process_records_input.checkpointer)
        except Exception as exc:
            self._log('Encountered an exception while processing records. '
                      'Exception was %r' % exc)

    def shutdown(self, shutdown_input):
        try:
            if shutdown_input.reason == 'TERMINATE':
                self._log('Was told to terminate, attempting to checkpoint.')
                self.checkpoint(shutdown_input.checkpointer, force=True)
            else:  # reason == 'ZOMBIE'
                self._log('Shutting down. Will not checkpoint.')
        except Exception as exc:
            self._log('Encountered an exception while shutting down. '
                      'Exception was %r' % exc)
