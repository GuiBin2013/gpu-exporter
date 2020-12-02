import time
import traceback

import tornado.web
from prometheus_client import REGISTRY, exposition
from prometheus_client.core import Gauge

from gpu import GpuCollection
from container import Container

gpu_data = dict()


class CustomGauge(Gauge):

    def clear_all(self):
        with self._lock:
            self._metrics.clear()


update_time = Gauge(
    "update_time",
    "update_time",
    (),
)

nvidia_gpu_num_devices = Gauge(
    "nvidia_gpu_num_devices",
    "nvidia_gpu_num_devices",
    ()
)

nvidia_gpu_duty_cycle = CustomGauge(
    "nvidia_gpu_duty_cycle",
    "nvidia_gpu_duty_cycle",
    ("minor_number", "name", "uuid")
)

nvidia_gpu_memory_total_bytes = CustomGauge(
    "nvidia_gpu_memory_total_bytes",
    "nvidia_gpu_memory_total_bytes",
    ("minor_number", "name", "uuid")
)

nvidia_gpu_memory_used_bytes = CustomGauge(
    "nvidia_gpu_memory_used_bytes",
    "nvidia_gpu_memory_used_bytes",
    ("minor_number", "name", "uuid")
)

nvidia_gpu_temperature_celsius = CustomGauge(
    "nvidia_gpu_temperature_celsius",
    "nvidia_gpu_temperature_celsius",
    ("minor_number", "name", "uuid")
)

container_nvidia_gpu_memory_used_bytes = CustomGauge(
    "container_nvidia_gpu_memory_used_bytes",
    "container_nvidia_gpu_memory_used_bytes",
    ("minor_number", "container_name", "container_id", "pid", "cmd", "since_time")
)


class MetricsHandler(tornado.web.RequestHandler):
    """
    Tornado ``Handler`` that serves prometheus metrics.
    """

    def clear_metrics(self):
        nvidia_gpu_duty_cycle.clear_all()
        nvidia_gpu_memory_total_bytes.clear_all()
        nvidia_gpu_memory_used_bytes.clear_all()
        nvidia_gpu_temperature_celsius.clear_all()
        container_nvidia_gpu_memory_used_bytes.clear_all()

    def initialize(self, registry=REGISTRY):
        self.registry = registry

    def get(self):

        if not gpu_data:
            self.write("error")
            return

        base_list = gpu_data["base_list"]
        processes = gpu_data["processes"]
        nvidia_gpu_num_devices.set(len(base_list))
        self.clear_metrics()
        for data in base_list:
            nvidia_gpu_duty_cycle.labels(minor_number=data["index"], name=data["name"], uuid=data["uuid"]).set(
                data["utilization.gpu"])
            nvidia_gpu_memory_total_bytes.labels(minor_number=data["index"], name=data["name"], uuid=data["uuid"]).set(
                data["memory.total"] * 1024 * 1024)
            nvidia_gpu_memory_used_bytes.labels(minor_number=data["index"], name=data["name"], uuid=data["uuid"]).set(
                data["memory.used"] * 1024 * 1024)
            nvidia_gpu_temperature_celsius.labels(minor_number=data["index"], name=data["name"], uuid=data["uuid"]).set(
                data["temperature.gpu"])
        for pid, data in processes.items():
            ps = data["processes"]  # list
            for p in ps:
                container_nvidia_gpu_memory_used_bytes.labels(
                    minor_number=p["index"],
                    container_name=data["container_name"],
                    container_id=data["container_id"],
                    pid=pid,
                    cmd=p["command"],
                    since_time=data["since_time"]
                ).set(p["gpu_memory_usage"] * 1024 * 1024)
        encoder, content_type = exposition.choose_encoder(self.request.headers.get('Accept'))
        self.set_header('Content-Type', content_type)
        self.write(encoder(self.registry))


def collect_gpu_data(interval=5):
    # 定时收集
    global gpu_data
    while True:
        try:
            gpu = GpuCollection()
            gpu.query()
            con = Container()
            result = con.query(set(gpu.processes))
            gpu_data["base_list"] = gpu.base_list
            gpu_data["processes"] = dict()
            for k, v in result.items():
                gpu_data["processes"][k] = v
                gpu_data["processes"][k]["processes"] = gpu.processes[k]
            update_time.set(int(time.time()))
        except Exception:
            gpu_data.clear()
            traceback.print_exc()
        finally:
            time.sleep(interval)
