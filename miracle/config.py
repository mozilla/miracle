import base64
from datetime import date
import os

from alembic.config import Config as AlembicConfig

TESTING = 'TESTING' in os.environ

# Hard end date for data being submitted to the service.
END_DATE = date(2016, 11, 22)  # Tentative... will change based on launch.

HERE = os.path.dirname(__file__)
STATIC_DIR = os.path.abspath(os.path.join(HERE, 'static'))
VERSION_FILE = os.path.join(STATIC_DIR, 'version.json')

DATA_DIR = os.path.abspath(os.path.join(HERE, os.pardir, 'data'))
BLOOM_DOMAIN = os.path.join(DATA_DIR, 'domain_blocklist.dat')
BLOOM_DOMAIN_SOURCE = os.path.join(DATA_DIR, 'domain_blocklist.txt')

DB_ROOT_CERT = os.environ.get('DB_ROOT_CERT', 'rds_root_ca.pem')
if TESTING:
    DB_ROOT_CERT = 'postgres_dev_ssl.pem'
DB_ROOT_CERT = os.path.join(DATA_DIR, DB_ROOT_CERT)

DB_USER = os.environ.get('DB_USER', 'miracle')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'miracle')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'miracle')
DB_URI = (
    'postgresql+psycopg2://%s:%s@%s:5432/%s?'
    'client_encoding=utf8&sslmode=verify-ca&sslrootcert=%s') % (
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_ROOT_CERT)

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = 'redis://%s:6379/%s' % (REDIS_HOST, REDIS_DB)

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
STATSD_HOST = os.environ.get('STATSD_HOST', 'localhost')

ALEMBIC_CFG = AlembicConfig()
ALEMBIC_CFG.set_section_option('alembic', 'script_location', 'miracle/alembic')
ALEMBIC_CFG.set_section_option('alembic', 'sqlalchemy.url', DB_URI)

PRIVATE_KEY = os.environ.get('PRIVATE_KEY')
PUBLIC_KEY = os.environ.get('PUBLIC_KEY')

if not PRIVATE_KEY and not PUBLIC_KEY:
    # Provide keys for testing and local development.
    with open(os.path.join(DATA_DIR, 'test_key.pem'), 'rb') as fd:
        PRIVATE_KEY = base64.b64encode(fd.read())
    with open(os.path.join(DATA_DIR, 'test_key.pem.pub'), 'rb') as fd:
        PUBLIC_KEY = base64.b64encode(fd.read())
