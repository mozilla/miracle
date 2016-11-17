import multiprocessing

errorlog = '-'
keepalive = 0
loglevel = 'warning'
max_requests = 100000
max_requests_jitter = max_requests // 10
timeout = 60
worker_class = 'miracle.web.worker.GeventWorker'
worker_connections = 20
workers = multiprocessing.cpu_count()


def post_worker_init(worker):  # pragma: no cover
    # Apply psycopg2 gevent patch.
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
    worker.wsgi(None, None)


def worker_exit(server, worker):  # pragma: no cover
    from miracle.web.app import worker_exit
    worker_exit(server, worker)


# cleanup
del multiprocessing
