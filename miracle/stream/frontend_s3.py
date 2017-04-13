import sys

from amazon_kclpy import kcl
from amazon_kclpy.v2 import processor


class RecordProcessor(processor.RecordProcessorBase):

    def __init__(self):
        pass

    def initialize(self, initialize_input):
        pass

    def process_records(self, process_records_input):
        for record in process_records_input.records:
            data = record.binary_data
            sys.stderr.write('Record processed: %s\n' % data.encode('ascii'))
        sys.stderr.flush()

    def shutdown(self, shutdown_input):
        pass


if __name__ == "__main__":
    kcl_process = kcl.KCLProcess(RecordProcessor())
    kcl_process.run()
