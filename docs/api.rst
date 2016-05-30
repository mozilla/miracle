===
API
===

The contextgraph service provides two API endpoints. One to share your
data with and upload it to the service. Another one to ask the service
to forget and delete all data about you.


Upload
======

To upload your data to the service, you can do a HTTPS POST request to
the ``/v1/upload`` API endpoint.

You need to send your unique user id (a UUID 4) in a ``X-User`` header.

.. code-block:: bash

    curl -H 'X-User: a6c6fc926dbd465fb200905cb1abe5c1' \
        https://contextgraph.dev.mozaws.net/v1/upload -d '{"some": "data"}'

If the data was accepted, you get a `200` response code.

If the request was malformed, you can get `4xx` responses, if the
service is unavailable or broken, you might get `5xx` responses.


Delete
======

To delete your data from the service, you can do a HTTPS POST request to
the ``/v1/delete`` API endpoint.

You need to send your unique user id (a UUID 4) in a ``X-User`` header.

.. code-block:: bash

    curl -H 'X-User: a6c6fc926dbd465fb200905cb1abe5c1' \
        https://contextgraph.dev.mozaws.net/v1/delete -d ''

If the delete request was accepted, you get a `200` response code.

If the request was malformed, you can get `4xx` responses, if the
service is unavailable or broken, you might get `5xx` responses.
