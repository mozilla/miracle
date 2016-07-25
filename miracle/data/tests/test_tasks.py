# -*- coding: utf-8 -*-

import pytest

from miracle.data import tasks


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


def test_delete(cache, celery, stats):
    cache.set(b'user_foo', b'')
    tasks.delete.delay('foo').get()
    assert b'user_foo' not in cache.keys()
