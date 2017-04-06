===
API
===

The miracle service provides a couple of API endpoint.

The main API endpoint allows you to share your data with and
upload it to the service.


JWK
===

The service requires you to send in any data in an encrypted form
using JWE encryption using the RSA-OAEP algorithm and A256GCM stream
encryption.

The service provides an endpoint exposing the public RSA key you need
to use in JWK format. You can issue a HTTPS GET request to ``/v2/jwk``
to get the key:

.. code-block:: bash

    curl https://miracle.services.mozilla.com/v2/jwk

The response contains a JSON body, of the form:

.. code-block:: javascript

    {"e": "AQAB", "kty": "RSA", "n": "..."}


Upload
======

To upload your data to the service, you can do a HTTPS POST request to
the ``/v2/upload`` API endpoint.

.. code-block:: bash

    curl -H 'Content-Type: text/plain' \
        https://miracle.services.mozilla.com/v2/upload -d '<data>'

If the data was accepted, you get a `200` response code.

If the request was malformed, you can get `4xx` responses and you
should discard the data.

If the service is unavailable or broken, you might get `5xx` responses
and you should retry the request after a back-off interval.


Payload
-------

The payload data is expected to be an JWE encrypted blob, using the
service provided public key. The algorithm needs to be RSA-OAEP with
A256GCM encryption.

The data inside the blob is a stringified JSON mapping with the
following structure:

.. code-block:: javascript

    {"user": "a6c6fc926dbd465fb200905cb1abe5c1",
     "something": "else"
    }

The user id is a client side generated UUID 4.

There can be any number of additional top-level keys with arbitrary
values, including additional nested mappings.
