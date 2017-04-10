import time


def test_kinesis(kinesis, raven):
    assert kinesis.ping(raven)

    kinesis.client.delete_stream(StreamName=kinesis.name)
    time.sleep(0.15)

    assert not kinesis.ping(raven)
    raven.check(['ResourceNotFoundException'])
