from pyramid.httpexceptions import HTTPServiceUnavailable
from pyramid.response import (
    FileResponse,
    Response,
)

from miracle.config import VERSION_FILE


def configure(config):
    config.add_view(heartbeat_view,
                    name='__heartbeat__', renderer='json')
    config.add_view(lbheartbeat_view,
                    name='__lbheartbeat__', renderer='json')

    config.add_view(index_view)
    config.add_view(robotstxt_view, name='robots.txt')
    config.add_view(version_view, name='__version__')


def heartbeat_view(request):
    cache_success = request.registry.cache.ping(request.registry.raven)

    if not cache_success:
        response = HTTPServiceUnavailable()
        response.content_type = 'application/json'
        response.json = {
            'cache': {'up': cache_success},
        }
        return response

    return {'cache': {'up': True}}


_INDEX_RESPONSE = '''\
<!DOCTYPE html><html><head>
<meta charset="UTF-8" />
<title>Mozilla Miracle</title>
</head><body>
<h1>Mozilla Miracle</h1>
<p>For more information about this service please
<a href="https://wiki.mozilla.org/Context_Graph">
visit the Context Graph Wiki</a>.
</p>
</body></html>
'''


def index_view(request):
    return Response(content_type='text/html', body=_INDEX_RESPONSE)


def lbheartbeat_view(request):
    return {'status': 'OK'}


_ROBOTS_RESPONSE = '''\
User-agent: *
Disallow: /__heartbeat__
Disallow: /__lbheartbeat__
Disallow: /__version__
Disallow: /v1/delete
Disallow: /v1/jwk
Disallow: /v1/stats
Disallow: /v1/upload
'''


def robotstxt_view(context, request):
    return Response(content_type='text/plain', body=_ROBOTS_RESPONSE)


def version_view(request):
    return FileResponse(
        VERSION_FILE,
        content_type='application/json',
        request=request)
