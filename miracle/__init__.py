# Apply gevent monkey patches as early as possible.
from gevent.monkey import patch_all
from psycogreen.gevent import patch_psycopg

patch_all()
patch_psycopg()


VERSION = '1.1.7.dev0'
