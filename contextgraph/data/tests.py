from contextgraph.data import tasks


def test_dummy(celery):
    result = tasks.dummy.delay().get()
    assert result is True
