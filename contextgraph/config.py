import os

TESTING = 'TESTING' in os.environ
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_DB = '1' if TESTING else '0'
REDIS_URI = 'redis://%s:6379/%s' % (REDIS_HOST, REDIS_DB)
