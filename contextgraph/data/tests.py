import pytest

from contextgraph.data import tasks


def test_dummy(celery, stats):
    result = tasks.dummy.delay().get()
    assert result == 2
    result = tasks.dummy.delay().get()
    assert result == 4
    stats.check(timer=[
        ('task', 2, ['task:data.tasks.dummy']),
    ])


def test_error(celery, raven, stats):
    with pytest.raises(ValueError):
        tasks.error.delay().get()
    raven.check(['ValueError'])
    stats.check(timer=[
        ('task', 1, ['task:data.tasks.error']),
    ])
