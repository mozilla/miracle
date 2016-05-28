from contextgraph.data import tasks


def test_dummy(celery, stats):
    result = tasks.dummy.delay().get()
    assert result is True
    stats.check(timer=[
        ('task', 1, ['task:data.tasks.dummy']),
    ])
