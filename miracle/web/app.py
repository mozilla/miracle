from pyramid.config import Configurator
from pyramid.tweens import EXCVIEW

from miracle.api.views import configure as configure_api_views
from miracle.cache import create_cache
from miracle.db import create_db
from miracle.config import REDIS_URI
from miracle.log import (
    configure_logging,
    create_raven,
    create_stats,
)
from miracle.web.views import configure as configure_web_views

_APP = None


def application(environ, start_response):  # pragma: no cover
    global _APP
    if _APP is None:
        _APP = create_app()
        if environ is None and start_response is None:
            # Called as part of gunicorn's post_worker_init
            return _APP

    return _APP(environ, start_response)


def create_app(redis_uri=REDIS_URI, _cache=None, _db=None,
               _raven=None, _stats=None):
    configure_logging()
    raven = create_raven(transport='gevent', _raven=_raven)

    try:
        config = Configurator(settings={
            'redis_uri': redis_uri,
        })
        config.add_tween('miracle.log.log_tween_factory', under=EXCVIEW)

        configure_api_views(config)
        configure_web_views(config)

        config.registry.cache = create_cache(_cache=_cache)
        config.registry.db = create_db(_db=_db)
        config.registry.raven = raven
        config.registry.stats = create_stats(_stats=_stats)

        config.registry.cache.ping(config.registry.raven)
        config.registry.db.ping(config.registry.raven)

        wsgi_app = config.make_wsgi_app()
    except Exception:  # pragma: no cover
        raven.captureException()
        raise

    return wsgi_app


def shutdown_app(app):
    registry = getattr(app, 'registry', None)
    if registry is not None:
        registry.cache.close()
        del registry.cache
        registry.db.close()
        del registry.db
        del registry.raven
        registry.stats.close()
        del registry.stats


def worker_exit(server, worker):  # pragma: no cover
    shutdown_app(_APP)
