=================
Local Development
=================

A multiple-container Docker configuration is available to support
local development and CI testing.


Architecture
============

`miracle` is built as a containerized Docker application,
with a web and worker role, using the same application image.

See the deploy documentation for a list of services.

A `Docker Compose <https://docs.docker.com/compose/>`_ configuration is
included to streamline setup and management of those services for local
development. They are run alongside the application containers on a
single `Docker <https://docs.docker.com/>`_ host.

For local development AWS S3 is substituted with the API-compatible
minio/minio project and AWS Kinesis with Kinesalite.

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

In order to inspect the AWS storage, you can open a web browser::

    http://127.0.0.1:9000/minio/


Production
==========

In production you can connect to the services from inside a running
docker container.

First find out what the installed application version is::

    docker images | grep miracle

If the installed version is 2.0, the output should show::

    mozilla/miracle    2.0    eb9495318561    5 days ago    151.9 MB

To start a container based on that image, do::

    docker run -it --rm \
        -e "S3_BUCKET=..." -e "..." \
        mozilla/miracle:2.0 shell

Make sure to pass along all required environment variables via
either individual `-e` arguments or based on a `--env-file`.
