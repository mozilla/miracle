#!/bin/sh

exec celery -A miracle.worker.app:celery_app worker -P gevent -Ofair --no-execv --without-mingle --without-gossip
