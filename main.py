
import os
import time
import threading
import logging

from tornado import web, ioloop

from container import Container
from gpu import GpuCollection
from metrics_http import MetricsHandler, collect_gpu_data

url_handlers = [
    ('/metrics', MetricsHandler),
    ("/", web.RedirectHandler, {"url": "/metrics", "permanent": False}),
]

if __name__ == "__main__":
    # check nvidia-smi
    port = int(os.getenv("port", "9439"))
    interval = int(os.getenv("interval", "5"))
    logging.info("check nvidia")
    gpu = GpuCollection()
    gpu.check_gpu()
    logging.info("check docker")
    # check docker
    con = Container()
    con.check_docker()
    t = threading.Thread(target=collect_gpu_data, args=(interval,))
    t.setDaemon(True)
    t.start()
    time.sleep(1)
    application = web.Application(url_handlers)
    logging.info("listen to the 0.0.0.0:port {0}".format(port))
    application.listen(port)
    ioloop.IOLoop.current().start()  # web启动
