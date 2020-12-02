
import docker
import json
import psutil
from datetime import datetime


class Container:

    def __init__(self):
        self._cli = docker.from_env()

    def query(self, pids : set = None) -> dict:
        containers = self._cli.containers.list()  # may be spend lots of time
        result = dict()
        for c in containers:
            processes = c.top()
            if processes:
                for p in processes["Processes"]:
                    # each
                    # ['UID', 'PID', 'PPID', 'C', 'STIME', 'TTY', 'TIME', 'CMD']
                    pid = int(p[1])
                    if pid in pids:
                        create_time = datetime.fromtimestamp(psutil.Process(pid).create_time()).strftime("%Y-%m-%d %H:%M:%S")
                        result[pid] = {"container_name": c.name, "container_id": c.id, "since_time": create_time}
        return result

    def check_docker(self):
        print(json.dumps(self._cli.info(), indent=2))


if __name__ == '__main__':
    from gpu import GpuCollection
    gpu = GpuCollection()
    gpu.query()
    print(gpu.processes)
    con = Container()
    d = con.query(set(gpu.processes))
    for k,v in d.items():
        print(v)
