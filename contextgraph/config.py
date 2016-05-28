import os

TESTING = 'TESTING' in os.environ

HERE = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(HERE, 'static'))
VERSION_FILE = os.path.join(STATIC_DIR, 'version.json')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = 'redis://%s:6379/%s' % (REDIS_HOST, REDIS_DB)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')
