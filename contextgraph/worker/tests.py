

def test_config(celery):
    assert celery.conf['CELERY_ALWAYS_EAGER']
    assert 'redis' in celery.conf['CELERY_RESULT_BACKEND']
    assert hasattr(celery, 'redis_client')
