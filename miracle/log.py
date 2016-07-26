from collections import deque
import logging
import time

from datadog.dogstatsd.base import DogStatsd
from pyramid.httpexceptions import (
    HTTPException,
    HTTPClientError,
)
from raven import Client as RavenClient
from raven.transport.gevent import GeventedHTTPTransport
from raven.transport.http import HTTPTransport
from raven.transport.threaded import ThreadedHTTPTransport

from miracle import VERSION
from miracle.config import (
    STATSD_HOST,
    SENTRY_DSN,
    TESTING,
)

# Mapping of raven transport names to classes.
RAVEN_TRANSPORTS = {
    'gevent': GeventedHTTPTransport,
    'sync': HTTPTransport,
    'threaded': ThreadedHTTPTransport,
}

SKIP_LOGGING = frozenset((
    '/__lbheartbeat__',
    '/__version__',
    '/robots.txt',
))


def configure_logging():
    """Configure basic Python logging."""
    logging.basicConfig(
        format='%(asctime)s - %(levelname)-5.5s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def log_tween_factory(handler, registry):

    def log_tween(request):
        if (request.path in SKIP_LOGGING):
            try:
                return handler(request)
            except HTTPException:  # pragma: no cover
                raise
            except Exception:  # pragma: no cover
                registry.raven.captureException()
                raise

        start = time.time()

        def _send(status):
            duration = int(round((time.time() - start) * 1000))
            tags = [
                # Convert a URI to a statsd acceptable metric name
                'path:%s' % request.path.replace(
                    '/', '.').lstrip('.').replace('@', '-'),
                'method:%s' % request.method.lower(),
                'status:%s' % status,
            ]
            registry.stats.timing('request', duration, tags=tags)
            registry.stats.increment('request', tags=tags)

        try:
            response = handler(request)
            _send(response.status_code)
            return response
        except HTTPClientError:
            # ignore general client side errors
            raise
        except Exception as exc:  # pragma: no cover
            if isinstance(exc, HTTPException):
                status = exc.status_code
            else:
                status = 500
            _send(status)
            registry.raven.captureException()
            raise

    return log_tween


def create_raven(sentry_dsn=SENTRY_DSN, transport='sync', _raven=None):
    if _raven is not None:
        return _raven

    klass = DebugRavenClient if TESTING else RavenClient
    client = klass(
        dsn=sentry_dsn,
        transport=RAVEN_TRANSPORTS[transport],
        release=VERSION)

    return client


def create_stats(statsd_host=STATSD_HOST, _stats=None):
    if _stats is not None:
        return _stats

    klass = DebugStatsClient if TESTING else StatsClient
    namespace = None if TESTING else 'miracle'
    client = klass(
        host=statsd_host, port=8125,
        namespace=namespace, use_ms=True)

    return client


class DebugRavenClient(RavenClient):

    def __init__(self, *args, **kw):
        super(DebugRavenClient, self).__init__(*args, **kw)
        self.msgs = deque(maxlen=100)

    def is_enabled(self):
        return True

    def send(self, auth_header=None, **data):
        self.msgs.append(data)
        self.state.set_success()

    def clear(self):
        self.msgs.clear()
        self.context.clear()

    def check(self, expected=()):  # pragma: no cover
        messages = [msg['message'] for msg in self.msgs]
        matched_msgs = []
        for exp in expected:
            count = 1
            name = exp
            if isinstance(exp, tuple):
                name, count = exp
            matches = [msg for msg in self.msgs
                       if msg['message'].startswith(name)]
            matched_msgs.extend(matches)
            assert len(matches) == count, messages

        for msg in matched_msgs:
            self.msgs.remove(msg)


class StatsClient(DogStatsd):

    def close(self):
        if self.socket:  # pragma: no cover
            self.socket.close()
            self.socket = None


class DebugStatsClient(StatsClient):

    def __init__(self, *args, **kw):
        super(DebugStatsClient, self).__init__(*args, **kw)
        self.msgs = deque(maxlen=100)

    def _send_to_server(self, packet):
        self.msgs.append(packet)

    def _find_messages(self, msg_type, msg_name,
                       msg_value=None, msg_tags=()):  # pragma: no cover
        data = {
            'counter': [],
            'timer': [],
            'gauge': [],
            'histogram': [],
            'set': [],
        }
        for msg in self.msgs:
            tags = ()
            if '|#' in msg:
                parts = msg.split('|#')
                tags = parts[-1].split(',')
                msg = parts[0]
            suffix = msg.split('|')[-1]
            name, value = msg.split('|')[0].split(':')
            value = int(value)
            if suffix == 'g':
                data['gauge'].append((name, value, tags))
            elif suffix == 'ms':
                data['timer'].append((name, value, tags))
            elif suffix.startswith('c'):
                data['counter'].append((name, value, tags))
            elif suffix == 'h':
                data['histogram'].append((name, value, tags))
            elif suffix == 's':
                data['set'].append((name, value, tags))

        result = []
        for msg in data.get(msg_type):
            if msg[0] == msg_name:
                if msg_value is None or msg[1] == msg_value:
                    if not msg_tags or msg[2] == msg_tags:
                        result.append((msg[0], msg[1], msg[2]))
        return result

    def clear(self):
        self.msgs.clear()

    def check(self, total=None, **kw):  # pragma: no cover
        if total is not None:
            assert total == len(self.msgs)

        for (msg_type, preds) in kw.items():
            for pred in preds:
                match = 1
                value = None
                tags = ()
                if isinstance(pred, str):
                    name = pred
                elif isinstance(pred, tuple):
                    if len(pred) == 2:
                        (name, match) = pred
                        if isinstance(match, list):
                            tags = match
                            match = 1
                    elif len(pred) == 3:
                        (name, match, value) = pred
                        if isinstance(value, list):
                            tags = value
                            value = None
                    elif len(pred) == 4:
                        (name, match, value, tags) = pred
                    else:
                        raise TypeError('wanted 2, 3 or 4 tuple, got %s'
                                        % type(pred))
                else:
                    raise TypeError('wanted str or tuple, got %s'
                                    % type(pred))
                msgs = self._find_messages(msg_type, name, value, tags)
                if isinstance(match, int):
                    assert match == len(msgs), self.msgs
