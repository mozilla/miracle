import multiprocessing
import os

testing = bool('TESTING' in os.environ)

# Enable eager execution in tests.
CELERY_ALWAYS_EAGER = testing
CELERY_EAGER_PROPAGATES_EXCEPTIONS = testing

# Based on Celery / Redis caveats
# celery.rtfd.org/en/latest/getting-started/brokers/redis.html#caveats
CELERY_REDIS_MAX_CONNECTIONS = 20
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
CELERYD_CONCURRENCY = multiprocessing.cpu_count()
CELERYD_MAX_TASKS_PER_CHILD = 100000
CELERYD_PREFETCH_MULTIPLIER = 8
CELERY_DISABLE_RATE_LIMITS = True
CELERY_MESSAGE_COMPRESSION = 'gzip'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'

# cleanup
del multiprocessing
del os
del testing
