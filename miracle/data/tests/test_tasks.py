# -*- coding: utf-8 -*-

import pytest

from miracle.data import tasks


def test_error(celery, raven, stats):
    with pytest.raises(ValueError):
        tasks.error.delay('secret').get()
    stats.check(timer=[
        ('task', 1, ['task:data.tasks.error']),
    ])
    msgs = list(raven.msgs)
    raven.check(['ValueError'])
    assert 'secret' not in repr(msgs[0])
    assert '<removed>' in repr(msgs[0])
