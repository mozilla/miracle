

def test_kinesis(kinesis, raven):
    assert kinesis.ping(raven)

    kinesis._delete_frontend_stream()

    assert not kinesis.ping(raven)
    raven.check(['ResourceNotFoundException'])
