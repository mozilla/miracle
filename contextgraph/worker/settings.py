import os

testing = bool(os.environ.get('TESTING', False))

# Enable eager execution in tests.
CELERY_ALWAYS_EAGER = testing
CELERY_EAGER_PROPAGATES_EXCEPTIONS = testing

# Based on Celery / Redis caveats
# celery.rtfd.org/en/latest/getting-started/brokers/redis.html#caveats
BROKER_TRANSPORT_OPTIONS = {
    'fanout_patterns': True,
    'fanout_prefix': True,
    'visibility_timeout': 3600,
}

CELERY_DEFAULT_QUEUE = 'celery_default'

CELERY_IMPORTS = [
    'contextgraph.data.tasks',
]

# Optimization
CELERYD_PREFETCH_MULTIPLIER = 8
CELERY_DISABLE_RATE_LIMITS = True
CELERY_MESSAGE_COMPRESSION = 'gzip'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# cleanup
del testing
del os
