=======
Metrics
=======

The application emits various metrics via StatsD.


HTTP
====

Each HTTP request emits a counter and timer metric called ``request``.
The timer counts the time in milliseconds it took to process the request.

Each request metric is tagged with:

    - ``path``: The URL path, e.g. ``v1.upload``
    - ``method``: The request method, e.g. ``post``
    - ``status``: The response code, e.g. ``200``


Task
====

Each asynchronous Celery task emits a timer called ``task``, which
measures the task execution time in milliseconds.

Each task metric is tagged with:

    - ``task``: The task function, e.g. ``data.tasks.upload``


Data
====

Upload
------

Each data upload emits a variety of metrics, depending on the data
it gets.

In case an error occurred during the upload or the data was invalid,
a counter called ``data.upload.error` will be emitted. It will be
tagged with a ``reason:<value>`` tag with one of the following values:

    - ``reason:encryption``: The data was not correctly encrypted.
    - ``reason:json``: The data was not valid JSON.
    - ``reason:validation``: The data didn't match the schema.
    - ``reason:db``: The data couldn't be inserted into the db.

For successful and valid data uploads, additional metrics capture facts
about the data itself:

    - ``data.user.new``: A new user has contributed data.

    - ``data.url.drop``: A number of URLs were filtered out / dropped.
    - ``data.url.new``: A number of new URLs were first recorded.

    - ``data.session.drop``: A number of sessions were filtered out.
    - ``data.session.new``: A number of new sessions were recorded.
