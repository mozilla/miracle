from miracle.stream.kcl import run_kcl_process


def process_frontend_s3(processor, records):
    seq = None
    sub_seq = None
    for record in records:
        data = record.binary_data
        seq = record.sequence_number
        sub_seq = record.sub_sequence_number
        processor._log('Processed data: %r' % data)
    return (seq, sub_seq)


if __name__ == "__main__":  # pragma: no cover
    run_kcl_process(process_frontend_s3, batch_size=10)
