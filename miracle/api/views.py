import json
import random

import botocore
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPMethodNotAllowed,
    HTTPServiceUnavailable,
)
from pyramid.response import Response


def configure(config):
    JWKView.configure(config)
    UploadView.configure(config)


class View(object):

    _renderer = 'json'
    _route_name = None
    _route_path = None

    _cors_headers = {
        'Access-Control-Allow-Headers': 'Content-Type, X-User',
        'Access-Control-Allow-Methods': '',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Max-Age': str(86400 * 30),  # 30 days
    }
    _supported_methods = ('POST', 'PUT')
    _unsupported_methods = ('GET', 'DELETE', 'PATCH')

    @classmethod
    def configure(cls, config):
        config.add_route(cls._route_name, cls._route_path)
        config.add_view(cls,
                        route_name=cls._route_name,
                        renderer=cls._renderer,
                        request_method=cls._supported_methods)
        config.add_view(cls,
                        attr='head',
                        route_name=cls._route_name,
                        request_method='HEAD')
        config.add_view(cls,
                        attr='options',
                        route_name=cls._route_name,
                        request_method='OPTIONS')
        config.add_view(cls,
                        attr='unsupported',
                        route_name=cls._route_name,
                        request_method=cls._unsupported_methods)

    def __init__(self, request):
        self.request = request
        self.request.response.headers.update(self.cors_headers)

    def __call__(self):
        raise NotImplementedError()

    @property
    def cors_headers(self):
        supported = self._supported_methods + ('HEAD', 'OPTIONS')
        cors_headers = self._cors_headers.copy()
        cors_headers['Access-Control-Allow-Methods'] = ', '.join(supported)
        return cors_headers

    def head(self):
        return Response()

    def options(self):
        return Response(headers=self.cors_headers)

    def unsupported(self):
        raise HTTPMethodNotAllowed()


class JWKView(View):

    _route_name = 'v2_jwk'
    _route_path = '/v2/jwk'

    _supported_methods = ('GET', )
    _unsupported_methods = ('POST', 'PUT', 'DELETE', 'PATCH')

    def __call__(self):
        jwk = self.request.registry.crypto._public_jwk
        data = jwk.export(private_key=False)
        return json.loads(data)


class UploadView(View):

    _route_name = 'v2_upload'
    _route_path = '/v2/upload'

    _max_size = 1024 * 1024  # 1 mib

    def __call__(self):
        body = self.request.body
        if not body:
            return HTTPBadRequest('Empty body.')

        if len(body) > self._max_size:
            return HTTPBadRequest('Encrypted body too large.')

        try:
            text = body.decode('ascii')
        except UnicodeDecodeError:
            return HTTPBadRequest('Invalid character encoding.')

        if not self.request.registry.crypto.validate(text):
            return HTTPBadRequest('Invalid JWE structure.')

        # Random partition key, as all client data is encrypted.
        partition_key = '%05d' % random.randint(0, 2**16)

        kinesis = self.request.registry.kinesis
        try:
            kinesis.client.put_record(
                Data=body,
                PartitionKey=partition_key,
                StreamName=kinesis.frontend_stream,
            )
        except botocore.exceptions.ClientError:
            self.request.registry.raven.captureException()
            return HTTPServiceUnavailable('Data queue backend unavailable.')

        return {'status': 'success'}
