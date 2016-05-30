=================
Local Development
=================

A multiple-container Docker configuration is available to support
local development.


Architecture
============

`contextgraph-service` is built as a containerized Docker application,
but to run it, several additional services are required:

- a `Celery <http://www.celeryproject.org/>`_ task queue
- a `Redis <http://redis.io/>`_ broker for the task queue

A `Docker Compose <https://docs.docker.com/compose/>`_ configuration is
included to streamline setup and management of those services for local
development. They are run alongside the application container on a
single `Docker Machine <https://docs.docker.com/machine/overview/>`_ VM.


Usage
=====

A `./server` utility script is included to streamline use of the Docker
containers.


First-Time Setup
================

First, run the following script:

.. code-block:: bash

    ./server init

This creates a host VM called `contextgraph-service-dev`.
Then, it configures a consistent hostname
(`contextgraph-service.dev <http://contextgraph-service.dev/>`_)
for local development (requires `sudo` to change `/etc/hosts`).

Once you have a running VM, you need to configure your shell to talk
to the right Docker daemon inside the VM:

.. code-block:: bash

    eval $(docker-machine env contextgraph-service-dev)


Development
===========

Finally, you're ready to go. The `./server` script has a number of
additional commands to help out.

- `./server start` - builds and starts the application and supporting services.
- `./server stop` - kills and removes all containers.
- `./server restart` - runs `./server stop`, then `./server start`.
- `./server shell` - Opens a shell inside the application container.
- `./server test` - Runs all tests inside the application container.
