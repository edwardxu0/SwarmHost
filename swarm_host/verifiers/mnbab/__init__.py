import os

from .. import Verifier
from ..verifier_configs import VerifierConfigs


class MNBab(Verifier):
    def __init__(self, logger):
        super(MNBab, self).__init__(logger)
        self.__name__ = "mn-bab"
        self.logger = logger

        # TODO: fix this
        self.config_path = "mnbab_configs.json"

    def configure(self, property):
        vc = VerifierConfigs(self)
        vc.save_configs(self.config_path)

    def run(self, model_path, property, log_path):
        self.configure(property)
        artifact = property["artifact"]
        eps = property["eps"]
        img_id = property["id"]
        property_path = os.path.join(
            property["prop_dir"], f"{artifact}_{img_id}_{eps}.vnnlib"
        )
        time = property["time"]
        memory = property["memory"]

        cmd = f"$SwarmHost/scripts/run_mnbab.sh --config $OCTOPUS/{self.config_path} --onnx_path $OCTOPUS/{model_path} --vnnlib_path $OCTOPUS/{property_path} --timeout {time}"

        print(cmd)
        self.execute(cmd, log_path, time, memory)

    def analyze(self, log_path):
        with open(log_path, "r") as fp:
            lines = fp.readlines()

        veri_ans = None
        veri_time = None
        for l in lines[-100:]:
            if "Result: True" in l:
                veri_ans = "unsat"
            elif "Result: False" in l:
                veri_ans = "sat"

            if "Time:" in l:
                veri_time = float(l.split()[-1][:-1])

            if veri_ans and veri_time:
                break

        assert veri_ans and veri_time
        return veri_ans, veri_time
