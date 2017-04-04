

def test_config(celery):
    assert celery.conf['task_always_eager']
    assert 'redis' in celery.conf['broker_url']
    assert hasattr(celery, 'cache')
    assert hasattr(celery, 'crypto')
    assert hasattr(celery, 'db')
    assert hasattr(celery, 'raven')
    assert hasattr(celery, 'stats')
