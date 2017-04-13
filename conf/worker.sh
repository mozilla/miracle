#!/bin/sh

# TODO
# exec `amazon_kclpy_helper.py --print_command --properties kcl-frontend-s3.properties --java $JAVA_HOME/bin/java`
exec celery -A miracle.worker.app:celery_app worker
