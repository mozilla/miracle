#!/bin/sh

exec celery -A contextgraph.worker.app:celery_app worker -Ofair --no-execv --without-mingle --without-gossip
