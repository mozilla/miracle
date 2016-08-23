from datetime import datetime
import json

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPMethodNotAllowed,
)
from pyramid.response import Response

from miracle.config import END_DATE
from miracle.data import tasks


def configure(config):
    DeleteView.configure(config)
    JWKView.configure(config)
    StatsView.configure(config)
    UploadView.configure(config)


def check_end_date(end=END_DATE):
    if datetime.utcnow().date() >= end:
        raise HTTPForbidden('Experiment has ended.')


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

    def user(self):
        user = self.request.headers.get('X-User')
        if not user or len(user) < 3 or len(user) > 36:
            return None
        if isinstance(user, bytes):
            user = user.decode('ascii')
        return user

    def head(self):
        return Response()

    def options(self):
        return Response(headers=self.cors_headers)

    def unsupported(self):
        raise HTTPMethodNotAllowed()


class DeleteView(View):

    _route_name = 'v1_delete'
    _route_path = '/v1/delete'

    def __call__(self):
        check_end_date()
        user = self.user()
        if not user:
            return HTTPBadRequest('Missing X-User header.')
        if self.request.body:
            return HTTPBadRequest('Non-empty body.')

        tasks.delete.delay(user)
        return {'status': 'success'}


class JWKView(View):

    _route_name = 'v1_jwk'
    _route_path = '/v1/jwk'

    _supported_methods = ('GET', )
    _unsupported_methods = ('POST', 'PUT', 'DELETE', 'PATCH')

    def __call__(self):
        jwk = self.request.registry.crypto._public_jwk
        data = jwk.export(private_key=False)
        return json.loads(data)


class StatsView(View):

    _route_name = 'v1_stats'
    _route_path = '/v1/stats'

    _supported_methods = ('GET', )
    _unsupported_methods = ('POST', 'PUT', 'DELETE', 'PATCH')

    def __call__(self):
        return {}


class UploadView(View):

    _route_name = 'v1_upload'
    _route_path = '/v1/upload'

    _max_size = 10 * 1024 * 1024  # 10 mib

    def __call__(self):
        check_end_date()
        user = self.user()
        if not user:
            return HTTPBadRequest('Missing or invalid X-User header.')

        body = self.request.body
        if not body:
            return HTTPBadRequest('Empty body.')

        if len(body) > self._max_size:
            return HTTPBadRequest('Uncompressed body too large.')

        try:
            text = body.decode('ascii')
        except UnicodeDecodeError:
            return HTTPBadRequest('Invalid character encoding.')

        if not self.request.registry.crypto.validate(text):
            return HTTPBadRequest('Invalid JWE structure.')

        tasks.upload.delay(user, text)
        return {'status': 'success'}
