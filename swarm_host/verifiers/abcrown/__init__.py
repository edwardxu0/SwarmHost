from .. import Verifier
from ..verifier_configs import VerifierConfigs


class ABCrown(Verifier):
    def __init__(self, logger):
        self.__name__ = "abcrown"
        self.logger = logger

        # TODO: fix this
        self.config_path = "abcrown.yml"

    def configure(self, property):
        vc = VerifierConfigs(self)
        print(vc.configs)
        vc.configs["data"]["dataset"] = property["artifact"]
        vc.configs["data"]["start"] = property["id"]
        vc.configs["data"]["end"] = property["id"] + 1
        vc.configs["specification"]["norm"] = property["norm"]
        vc.configs["specification"]["epsilon"] = property["eps"]
        vc.save_configs(self.config_path)

    def run(self, model_path, property, log_path):
        self.configure(property)
        time = property["time"]
        memory = property["memory"]
        cmd = f"$SwarmHost/scripts/run_abcrown.sh --config $OCTOPUS/{self.config_path} --onnx_path $OCTOPUS/{model_path} --timeout {time}"
        self.execute(cmd, log_path, time, memory)

    def analyze(self, log_path):
        with open(log_path, "r") as fp:
            lines = fp.readlines()

        veri_ans = None
        veri_time = None
        for l in lines[-100:]:
            if "total verified (safe/unsat): 1" in l:
                veri_ans = "unsat"
            elif "total falsified (unsafe/sat): 1" in l:
                veri_ans = "sat"
            elif "timeout: 1" in l:
                veri_ans = "timeout"
            elif "Time out!!!!!!!!" in l:
                veri_ans = "timeout"

            if "mean time for ALL instances (total 1):" in l:
                veri_time = float(l.split()[7][:-1])

            if veri_ans and veri_time:
                break

        assert veri_ans and veri_time
        return veri_ans, veri_time
