=================
Local Development
=================

A multiple-container Docker configuration is available to support
local development.


Architecture
============

`miracle` is built as a containerized Docker application,
but to run it, several additional services are required:

- a `Celery <http://www.celeryproject.org/>`_ task queue
- a `Redis <http://redis.io/>`_ broker for the task queue

A `Docker Compose <https://docs.docker.com/compose/>`_ configuration is
included to streamline setup and management of those services for local
development. They are run alongside the application container on a
single `Docker <https://docs.docker.com/>`_ host.


First-Time Setup
================

You need to install Docker and Docker Compose on your machine. If you
are on Mac OS, you need to install
`Docker for Mac <https://docs.docker.com/docker-for-mac/>`_.


Development
===========

A `./server` utility script is included to streamline use of the Docker
containers. It has a number of commands to help out:

- `./server start` - builds and starts all containers.
- `./server stop` - kills and removes all containers.
- `./server restart` - runs `./server stop`, then `./server start`.
- `./server shell` - Opens a shell inside the application container.
- `./server test` - Runs all tests inside the application container.
