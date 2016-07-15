#!/bin/sh

cd $(dirname $0)
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
        exec /bin/sh
        ;;
    test)
        echo "Running Tests"
        cd ..
        flake8 miracle
        TESTING=true py.test --cov-config=.coveragerc --cov=miracle miracle
        ;;
    alembic)
        echo "Running Alembic"
        cd ..
        alembic $2 $3 $4 $5 $6 $7 $8 $9
        ;;
    *)
        echo "Usage: $0 {web|worker|shell|test|alembic}"
        exit 1
esac
