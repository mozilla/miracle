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
        flake8 contextgraph
        TESTING=true py.test --cov-config=.coveragerc --cov=contextgraph contextgraph
        ;;
    *)
        echo "Usage: $0 {web|worker|shell|test}"
        exit 1
esac
