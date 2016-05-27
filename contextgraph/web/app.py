from pyramid.config import Configurator

from contextgraph.cache import create_cache
from contextgraph.config import REDIS_URI
from contextgraph.web import views

_APP = None


def application(environ, start_response):  # pragma: no cover
    global _APP
    if _APP is None:
        _APP = create_app()
        if environ is None and start_response is None:
            # Called as part of gunicorn's post_worker_init
            return _APP

    return _APP(environ, start_response)


def create_app(redis_uri=REDIS_URI, _cache=None):
    config = Configurator(settings={
        'redis_uri': redis_uri,
    })

    views.configure(config)

    config.registry.cache = create_cache(_cache=_cache)

    return config.make_wsgi_app()


def shutdown_app(app):
    registry = getattr(app, 'registry', None)
    if registry is not None:
        registry.cache.close()
        del registry.cache


def worker_exit(server, worker):  # pragma: no cover
    shutdown_app(_APP)
