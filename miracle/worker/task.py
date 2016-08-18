from celery import Task
from kombu.serialization import (
    dumps as kombu_dumps,
    loads as kombu_loads,
)


class BaseTask(Task):

    abstract = True
    acks_late = False
    ignore_result = True
    max_retries = 3

    def __call__(self, *args, **kw):
        """
        Execute the task, capture a statsd timer for the task duration and
        automatically report exceptions into Sentry.
        """
        name = self.name
        if name.startswith('miracle.'):
            name = name[8:]
        with self.stats.timed('task', tags=['task:' + name]):
            try:
                result = super(BaseTask, self).__call__(*args, **kw)
            except Exception as exc:
                self.raven.captureException()
                if not self.app.conf.CELERY_ALWAYS_EAGER:  # pragma: no cover
                    raise self.retry(exc=exc)
                raise
        return result

    def apply(self, *args, **kw):
        """
        This method is only used when calling tasks directly and blocking
        on them. It's also used if always_eager is set, like in tests.

        If always_eager is set, we feed the task arguments through the
        de/serialization process to make sure the arguments can indeed
        be serialized into JSON.
        """

        if self.app.conf.CELERY_ALWAYS_EAGER:
            # We do the extra check to make sure this was really used from
            # inside tests
            serializer = self.app.conf.CELERY_TASK_SERIALIZER
            content_type, encoding, data = kombu_dumps(args, serializer)
            args = kombu_loads(data, content_type, encoding)

        return super(BaseTask, self).apply(*args, **kw)

    @property
    def bloom_domain(self):
        return self.app.bloom_domain

    @property
    def cache(self):
        return self.app.cache

    @property
    def crypto(self):
        return self.app.crypto

    @property
    def db(self):
        return self.app.db

    @property
    def raven(self):
        return self.app.raven

    @property
    def stats(self):
        return self.app.stats
