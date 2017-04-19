from miracle.stream.kcl import (
    BaseRecordProcessor,
    run_kcl_process,
)


class RecordProcessor(BaseRecordProcessor):

    def _process_record(self, data, key, seq, sub_seq):
        # TODO Implement logic.
        self._log('Processed data: %r' % data)


if __name__ == "__main__":  # pragma: no cover
    run_kcl_process(RecordProcessor())
