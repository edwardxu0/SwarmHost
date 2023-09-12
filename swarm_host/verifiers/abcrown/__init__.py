import os

from .. import Verifier
from ..verifier_configs import VerifierConfigs


class ABCrown(Verifier):
    def __init__(self, verification_problem, beta=False):
        super().__init__(verification_problem)
        self.__name__ = "abcrown"
        self.beta = beta

    def configure(self):
        vc = VerifierConfigs(self)
        # print(vc.configs)
        if self.beta:
            vc.configs["solver"]["beta-crown"]["beta"] = True
        # print(vc.configs)
        vc.save_configs(self.verification_problem.paths["veri_config_path"])
        self.logger.debug(
            f"Verification config saved to: {self.verification_problem.paths['veri_config_path']}"
        )

    def run(self):
        self.configure()
        config_path = self.verification_problem.paths["veri_config_path"]
        property_path = self.verification_problem.property.property_path
        model_path = self.verification_problem.paths["model_path"]
        log_path = self.verification_problem.paths["veri_log_path"]

        time = self.verification_problem.verifier_config["time"]
        memory = self.verification_problem.verifier_config["memory"]

        cmd = f"$SwarmHost/scripts/run_abcrown.sh --config $OCTOPUS/{config_path} --onnx_path $OCTOPUS/{model_path} --vnnlib_path {property_path} --timeout {time}"
        self.execute(cmd, log_path, time, memory)

    def analyze(self):
        with open(self.verification_problem.paths["veri_log_path"], "r") as fp:
            lines = fp.readlines()

        veri_ans = None
        veri_time = None
        for l in lines[-100:]:
            if "Result: " in l:
                veri_ans = l.strip().split()[-1]
            elif "Time: " in l:
                veri_time = float(l.strip().split()[-1])

            if veri_ans and veri_time:
                break

        assert veri_ans and veri_time
        return veri_ans, veri_time
