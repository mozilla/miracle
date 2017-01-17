import os

testing = bool('TESTING' in os.environ)

# Enable eager execution in tests.
task_always_eager = testing
task_eager_propagates = testing

# Based on Celery / Redis caveats
# celery.rtfd.org/en/latest/getting-started/brokers/redis.html#caveats
redis_max_connections = 20
broker_transport_options = {
    'socket_connect_timeout': 60,
    'socket_keepalive': True,
    'socket_timeout': 30,
    'visibility_timeout': 43200,
}

task_default_queue = 'celery_default'
task_ignore_result = True

imports = [
    'miracle.data.tasks',
]

# Optimization
worker_max_tasks_per_child = 100000
worker_prefetch_multiplier = 8
worker_disable_rate_limits = True
task_compression = 'gzip'

accept_content = ['json']
result_serializer = 'json'
task_serializer = 'json'

# cleanup
del os
del testing
