from miracle.data import delete
from miracle.data import tasks


class DummyTask(object):

    def __init__(self, cache=None):
        self.cache = cache


def test_delete_data(cache):
    cache.set(b'user_foo', b'')
    task = DummyTask(cache=cache)
    assert delete.delete_data(task, 'foo')
    assert b'user_foo' not in cache.keys()


def test_delete_main(cache):
    def _delete(task, user):
        return user

    task = DummyTask(cache=cache)
    result = delete.main(task, 'foo', _delete_data=_delete)
    assert result == 'foo'


def test_task(celery):
    assert tasks.delete.delay('foo', _delete_data=False).get()


def test_task_fail(celery):
    assert not tasks.delete.delay('', _delete_data=False).get()
