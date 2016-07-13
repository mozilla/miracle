

def test_raven(raven):
    try:
        raise ValueError('foo')
    except ValueError:
        raven.captureException()
    raven.check(['ValueError'])


def test_stats_counter(stats):
    stats.increment('foo', 1)
    stats.increment('foo', 1)
    stats.increment('bar', 3, tags=['baz:11'])
    stats.check(counter=[
        ('foo', 2, 1),
        ('bar', 1, 3, ['baz:11']),
    ])


def test_stats_timer(stats):
    with stats.timed('foo', tags=['bar:abc']):
        stats.timing('foo', 10, tags=['bar:abc'])
    stats.check(timer=[
        ('foo', 2, ['bar:abc']),
    ])
