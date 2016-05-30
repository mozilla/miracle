from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPMethodNotAllowed,
)
from pyramid.response import Response

from contextgraph.exceptions import GZIPDecodeError
from contextgraph.util import gzip_decode


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
        if 'X-User' not in self.request.headers:
            return HTTPBadRequest('Missing X-User header.')
        if self.request.body:
            return HTTPBadRequest('Non-empty body.')
        return {'status': 'success'}


class UploadView(View):

    _route_name = 'v1_upload'
    _route_path = '/v1/upload'

    def __call__(self):
        body = self.request.body

        if 'X-User' not in self.request.headers:
            return HTTPBadRequest('Missing X-User header.')

        if not body:
            return HTTPBadRequest('Empty body.')

        if self.request.headers.get('Content-Encoding') == 'gzip':
            try:
                body = gzip_decode(body)
            except GZIPDecodeError:
                return HTTPBadRequest('Invalid GZIP body.')

        return {'status': 'success'}
