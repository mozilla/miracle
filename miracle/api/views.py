from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPMethodNotAllowed,
)
from pyramid.response import Response

from miracle.data import tasks
from miracle.exceptions import GZIPDecodeError
from miracle.util import gzip_decode


def configure(config):
    DeleteView.configure(config)
    UploadView.configure(config)


class View(object):

    _route_name = None
    _route_path = None

    _cors_headers = {
        'Access-Control-Allow-Headers':
            'Content-Encoding, Content-Type, X-User',
        'Access-Control-Allow-Methods': 'HEAD, OPTIONS, POST, PUT',
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
                        renderer='json',
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
        self.request.response.headers.update(self._cors_headers)

    def __call__(self):
        raise NotImplementedError()

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
        return Response(headers=self._cors_headers)

    def unsupported(self):
        raise HTTPMethodNotAllowed()


class DeleteView(View):

    _route_name = 'v1_delete'
    _route_path = '/v1/delete'

    def __call__(self):
        user = self.user()
        if not user:
            return HTTPBadRequest('Missing X-User header.')
        if self.request.body:
            return HTTPBadRequest('Non-empty body.')

        tasks.delete.delay(user)
        return {'status': 'success'}


class UploadView(View):

    _route_name = 'v1_upload'
    _route_path = '/v1/upload'

    _max_size = 10 * 1024 * 1024  # 10 mib

    def __call__(self):
        user = self.user()
        if not user:
            return HTTPBadRequest('Missing or invalid X-User header.')

        body = self.request.body
        if not body:
            return HTTPBadRequest('Empty body.')

        if self.request.headers.get('Content-Encoding') == 'gzip':
            try:
                body = gzip_decode(body, encoding=None)
            except GZIPDecodeError:
                return HTTPBadRequest('Invalid GZIP body.')

        if len(body) > self._max_size:
            return HTTPBadRequest('Uncompressed body too large.')

        tasks.upload.delay(user, body)
        return {'status': 'success'}
