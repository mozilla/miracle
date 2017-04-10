

def test_config(celery):
    assert celery.conf['task_always_eager']
    assert 'redis' in celery.conf['broker_url']
