from pyramid.httpexceptions import HTTPMethodNotAllowed

HTTP_METHODS = frozenset([
    'DELETE',
    'GET',
    'HEAD',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
])

HTTP_UPLOAD_METHODS = frozenset(['HEAD', 'POST', 'PUT'])


def configure(config):
    config.add_route('v1_delete', '/v1/delete')
    config.add_view(delete_view,
                    route_name='v1_delete',
                    renderer='json',
                    request_method=tuple(HTTP_UPLOAD_METHODS))
    config.add_view(unsupported_view,
                    route_name='v1_delete',
                    request_method=tuple(HTTP_METHODS - HTTP_UPLOAD_METHODS))

    config.add_route('v1_upload', '/v1/upload')
    config.add_view(upload_view,
                    route_name='v1_upload',
                    renderer='json',
                    request_method=tuple(HTTP_UPLOAD_METHODS))
    config.add_view(unsupported_view,
                    route_name='v1_upload',
                    request_method=tuple(HTTP_METHODS - HTTP_UPLOAD_METHODS))


def delete_view(request):
    return {'status': 'success'}


def unsupported_view(request):
    raise HTTPMethodNotAllowed()


def upload_view(request):
    return {'status': 'success'}
