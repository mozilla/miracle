import base64
import os

TESTING = 'TESTING' in os.environ

HERE = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(HERE, 'static'))
VERSION_FILE = os.path.join(STATIC_DIR, 'version.json')

DB_ENDPOINT = os.environ.get('DB_ENDPOINT')

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = 'redis://{host}:6379/{name}'.format(host=REDIS_HOST, name=REDIS_DB)

S3_BUCKET = os.environ.get('S3_BUCKET', 'net-mozaws-dev-miracle-test')
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', None)
SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')

if not PRIVATE_KEY and not PUBLIC_KEY:
    # Provide keys for testing and local development.
    DATA_DIR = os.path.abspath(os.path.join(HERE, os.pardir, 'data'))

    with open(os.path.join(DATA_DIR, 'test_key.pem'), 'rb') as fd:
        PRIVATE_KEY = base64.b64encode(fd.read())
    with open(os.path.join(DATA_DIR, 'test_key.pem.pub'), 'rb') as fd:
        PUBLIC_KEY = base64.b64encode(fd.read())
    del DATA_DIR
