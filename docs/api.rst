===
API
===

The miracle service provides a couple of API endpoints. The two primary
endpoints allow you to share your data with and upload it to the service.
The other allows you to ask the service to forget and delete all data
about you.


JWK
===

The service requires you to send in any data in an encrypted form
using JWE encryption using the RSA-OAEP algorithm and A256GCM stream
encryption.

The service provides an endpoint exposing the public RSA key you need
to use in JWK format. You can issue a HTTPS GET request to ``/v1/jwk``
to get the key:

.. code-block:: bash

    curl https://miracle.services.mozilla.com/v1/jwk

The response contains a JSON body, of the form:

.. code-block:: javascript

    {"e": "AQAB", "kty": "RSA", "n": "..."}


Upload
======

To upload your data to the service, you can do a HTTPS POST request to
the ``/v1/upload`` API endpoint.

You need to send your unique user id (a UUID 4) in a ``X-User`` header.

.. code-block:: bash

    curl -H 'X-User: a6c6fc926dbd465fb200905cb1abe5c1' \
        -H 'Content-Type: text/plain' \
        https://miracle.services.mozilla.com/v1/upload -d '<data>'

If the data was accepted, you get a `200` response code.

If the request was malformed, you can get `4xx` responses, if the
service is unavailable or broken, you might get `5xx` responses.


Payload
-------

The payload data is expected to be an JWE encrypted blob, using the
service provided public key. The algorithm needs to be RSA-OAEP with
A256GCM encryption.

The data inside the blob is a stringified JSON mapping with the
following structure:

.. code-block:: javascript

    {"sessions" : [
        {
            "url": "http://www.apple.com/path/to/something",
            "start_time": 1468616293,
            "duration": 2400
        }, {
            "url": "http://www.google.com/another/path/?argument=term",
            "start_time": 1468616317,
            "duration": 4400
        }
    ]}

A session in our context is specific to a single URL and describes the
interaction that happens between the user and that URL from the time
the user first opens the URL (starts the session) and the time the user
navigates away from the URL (ends the session). Closing a browser window
or closing the browser itself also ends the session.

The start_time is specified in timezone neutral Unix time.
The duration is measured in milliseconds.


Delete
======

To delete your data from the service, you can do a HTTPS POST request to
the ``/v1/delete`` API endpoint.

You need to send your unique user id (a UUID 4) in a ``X-User`` header.

.. code-block:: bash

    curl -H 'X-User: a6c6fc926dbd465fb200905cb1abe5c1' \
        https://miracle.services.mozilla.com/v1/delete -d ''

If the delete request was accepted, you get a `200` response code.

If the request was malformed, you can get `4xx` responses, if the
service is unavailable or broken, you might get `5xx` responses.


Stats
=====

To get general statistics from the service, you can do a HTTPS GET
request to the ``/v1/stats`` API endpoint.

.. code-block:: bash

    curl https://miracle.services.mozilla.com/v1/stats

The response contains a JSON body, with a mapping of metrics names
to values.
