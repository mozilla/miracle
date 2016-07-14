import os

TESTING = 'TESTING' in os.environ

HERE = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(HERE, 'static'))
VERSION_FILE = os.path.join(STATIC_DIR, 'version.json')

DB_USER = os.environ.get('DB_USER', 'miracle')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'miracle')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'miracle')
DB_URI = 'postgresql+psycopg2://%s:%s@%s:5432/%s' % (
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)


REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = 'redis://%s:6379/%s' % (REDIS_HOST, REDIS_DB)

S3_BUCKET = os.environ.get('S3_BUCKET', None)
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')
