from pyramid.config import Configurator

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


def create_app(redis_uri=REDIS_URI):
    config = Configurator(settings={
        'redis_uri': redis_uri,
    })

    views.configure(config)

    config.registry.redis_client = None

    return config.make_wsgi_app()


def shutdown_app(app):
    registry = getattr(app, 'registry', None)
    if registry is not None:
        del registry.redis_client


def worker_exit(server, worker):  # pragma: no cover
    shutdown_app(_APP)
