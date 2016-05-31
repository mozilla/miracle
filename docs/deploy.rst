==========
Deployment
==========

The service consists of a main web and celery worker docker container
and supporting services.

In a production environment the following services are typically used:

- Amazon ELB handling SSL termination
- Amazon EC2 running Docker containers for both web and worker roles
- Amazon ElastiCache Redis
- Amazon S3 for persistent storage
- Nginx running on the web role EC2 instances, proxying HTTP traffic
- A Datadog/StatsD daemon running on each EC2 instance
- An externally hosted Sentry service


Docker Image
============

The service is built upon a single docker image which is shared between
the web and worker roles.

The image contains an entrypoint that can take either "web" or "worker"
as the run command, defaulting to "web".

It exposes port 8000, which is only used by the web role.


Environment Variables
=====================

The docker image expects to get the app configuration via environment
variables.

Both roles expect:

* ``REDIS_HOST``, example ``example.cache.amazonaws.com``
* ``SENTRY_DSN``, example ``https://public:secret@sentry.example.com/id``
* ``STATSD_HOST``, example ``172.17.42.1``

The worker role additionally expects:

* ``S3_BUCKET``, example ``com-example-dev-us-west-2-contextgraph``


AWS Permissions
===============

Both roles expect to have access from inside the Docker containers
to the ElastiCache Redis instance, Sentry and the StatsD daemon.

Only the worker role should have access to the Amazon S3 bucket from
inside the docker container.

It needs both read and write access to its bucket, so permissions:

* ``s3:AbortMultipartUpload``
* ``s3:DeleteObject``
* ``s3:GetObject``
* ``s3:ListBucket``
* ``s3:ListBucketMultipartUploads``
* ``s3:ListMultipartUploadParts``
* ``s3:PutObject``


Web Role Configuration
======================

The HTTP/S flow generally is:

Internet --> ELB --> Nginx --> Web Server inside Docker Container

The docker container exposes the web server on port 8000 and it can
be bound at runtime to port 8000 on the EC2 host machine.

Typically an Nginx instance on the EC2 host will listen on port
80 and 443 for HTTP traffic and proxy pass both to port 8000.

The ELB listens on port 80 for HTTP and port 443 for HTTPS traffic
and handles SSL termination. It forwards both as HTTP-only traffic
to Nginx on port 80 and 443 respectively.

The ELB should use health checks and can use the ``/__lbheartbeat__``
endpoint supported by the application to do so.


Status Checks
=============

Both roles will try to connect to Redis during app startup, and send
an error report to Sentry if they fail.

The worker role will also try to connect to the S3 bucket and send
an error to Sentry if it fails.

The web role exposes three URL endpoints to check its status:

* ``__lbheartbeat__`` - Returns 200 OK if the web app is responding.
* ``__heartbeat__`` - Returns 200 OK if the web app can connect to Redis.
* ``__version__`` - Returns version data about the running software.
