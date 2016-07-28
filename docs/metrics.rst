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
that it gets.

In case an error occurred during the upload or the data was invalid,
one of the following counters will be emitted:

    - ``data.upload.error.json``: The data was not valid JSON.
    - ``data.upload.error.validation``: The data didn't match the schema.
    - ``data.upload.error.db``: The data couldn't be inserted into the db.

For successful and valid data uploads, additional metrics capture facts
about the data itself:

    - ``data.user.new``: A new user has contributed data.

    - ``data.url.drop``: A number of URLs was filtered out / dropped.
    - ``data.url.new``: A number of new URLs was first recorded.

    - ``data.session.drop``: A number of sessions was filtered out.
    - ``data.session.new``: A number of new sessions was recorded.

Delete
------

Data deletion tasks can emit a single metric:

    - ``data.user.delete``: An existing user was deleted.

This metric is only emitted if the user that we were asked to delete
did previously exist.
