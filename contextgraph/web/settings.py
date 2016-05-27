errorlog = '-'
keepalive = 0
loglevel = 'warning'
max_requests = 1000000
max_requests_jitter = max_requests // 10
timeout = 60
worker_class = 'contextgraph.web.worker.GeventWorker'
worker_connections = 20


def post_worker_init(worker):  # pragma: no cover
    worker.wsgi(None, None)


def worker_exit(server, worker):  # pragma: no cover
    from contextgraph.web.app import worker_exit
    worker_exit(server, worker)
