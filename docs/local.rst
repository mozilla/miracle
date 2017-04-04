=================
Local Development
=================

A multiple-container Docker configuration is available to support
local development and CI testing.


Architecture
============

`miracle` is built as a containerized Docker application,
with a web and worker role, using the same application image.
In addition several services are required:

- a `Redis <http://redis.io/>`_ cache
- a `Postgres <https://www.postgresql.org/>`_ database

A `Docker Compose <https://docs.docker.com/compose/>`_ configuration is
included to streamline setup and management of those services for local
development. They are run alongside the application containers on a
single `Docker <https://docs.docker.com/>`_ host.


First-Time Setup
================

You need to install Docker and Docker Compose on your machine. If you
are on Mac OS, you need to install
`Docker for Mac <https://docs.docker.com/docker-for-mac/>`_.


Development
===========

A `./server` utility script is included to streamline the use of the
Docker containers. It has a number of commands to help out:

- `./server start` - builds and starts all containers.
- `./server stop` - kills and removes all containers.
- `./server restart` - runs `./server stop`, then `./server start`.
- `./server shell` - Opens a shell inside the application container.
- `./server test` - Runs all tests inside the application container.
- `./server alembic` - Runs alembic inside the application container.

In order to inspect the database, you can open a shell inside the
running Postgres container::

    docker-compose exec postgres sh

And run commands like::

    pg_dump -U miracle miracle
    psql -U miracle miracle

To inspect and manipulate the Redis cache, open a shell::

    docker-compose exec redis sh

And open the Redis client::

    redis-cli


Production
==========

In production you can inspect the database from inside a running
docker container.

First find out what the installed application version is::

    docker images | grep miracle

If the installed version is 1.0.5, the output should show::

    mozilla/miracle    1.0.5    eb9495318562    5 days ago    151.9 MB

To start a container based on that image, do::

    docker run -it --rm \
        -e "DB_HOST=..." -e "DB_USER=..." -e "DB_PASSWORD=..." \
        mozilla/miracle:1.0.5 shell

The docker container includes a helper script to connect to the
Postgres database with all connection information taken from the
`DB_*` environment variables::

    ./db.sh -c "\d+"

Or open the prompt::

    ./db.sh
