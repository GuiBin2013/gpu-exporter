
import gpustat


class GpuCollection:

    def __init__(self):

        self.base_list = list()
        self.processes = dict()

    def query(self):
        r = self._query()
        result = r.jsonify()
        for d in result["gpus"]:
            processes = d.pop("processes")
            self.base_list.append(d)
            for p in processes:
                p["index"] = d["index"]
                pid = int(p["pid"])
                if p["pid"] not in self.processes:
                    self.processes[pid] = list()
                self.processes[pid].append(p)

    @staticmethod
    def _query():
        # nvidia-smi
        return gpustat.GPUStatCollection.new_query()

    @classmethod
    def check_gpu(cls):
        cls._query().print_json()


if __name__ == '__main__':
    g = GpuCollection()
    g.query()

    print(g.base_list)
    print(g.processes)
