#!/bin/sh

export GEVENT_RESOLVER=ares

cd $(dirname $0)
python kcl.py

case "$1" in
    web)
        echo "Starting Web Server"
        exec ./web.sh
        ;;
    worker)
        echo "Starting Celery Worker"
        exec ./worker.sh
        ;;
    shell)
        echo "Opening shell"
        cd ..
        exec /bin/bash
        ;;
    test)
        echo "Running Tests"
        cd ..
        TESTING=true pytest --cov-config=.coveragerc --cov=miracle \
            miracle $2 $3 $4 $5 $6 $7 $8 $9 && \
            flake8 miracle
        ;;
    *)
        echo "Usage: $0 {web|worker|shell|test}"
        exit 1
esac
