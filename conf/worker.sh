#!/bin/sh

exec celery -A miracle.worker.app:celery_app worker
