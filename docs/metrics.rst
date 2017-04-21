=======
Metrics
=======

The application emits various metrics via StatsD.


HTTP
====

Each HTTP request emits a counter and timer metric called ``request``.
The timer counts the time in milliseconds it took to process the request.

Each request metric is tagged with:

    - ``path``: The URL path, e.g. ``v2.upload``
    - ``method``: The request method, e.g. ``post``
    - ``status``: The response code, e.g. ``200``

Stream
======

Each processed stream record emits metrics.

Runtime
-------

These metrics are all taged with the the shard id (``shard:shard-0001``)
and the consumer name (``name:miracle.stream.module:function``).

The ``stream.checkpoint`` metric has an additional tag to capture
retried attempts, with ``try:1`` being the first.

    - ``stream.checkpoint``: A timer for `checkpointing`.
    - ``stream.process``: A timer for `process_records`.
    - ``stream.records``: A counter for the number of processed records.

Error
-----

In case an error occurred during the processing or the data was invalid,
a counter called ``stream.process.error` will be emitted. It will be
tagged with a ``reason:<value>`` tag with one of the following values:

    - ``reason:encryption``: The data was not correctly encrypted.
    - ``reason:json``: The data was not valid JSON.
    - ``reason:validation``: The data didn't match the schema.
