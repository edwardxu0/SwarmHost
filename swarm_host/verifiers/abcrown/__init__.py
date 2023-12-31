import os

from .. import Verifier
from ..verifier_configs import VerifierConfigs


class ABCrown(Verifier):
    def __init__(self, verification_problem, beta=False):
        super().__init__(verification_problem)
        self.__name__ = "ABCrown"
        self.beta = beta

    def configure(self, config_path):
        vc = VerifierConfigs(self)
        if self.beta:
            vc.configs["solver"]["beta-crown"]["beta"] = True
        vc.save_configs(config_path)
        self.logger.debug(f"Verification config saved to: {config_path}")

    def run(self, config_path, model_path, property_path, log_path, time, memory):

        cmd = f"$SwarmHost/scripts/run_abcrown.sh --config {config_path} --onnx_path {model_path} --vnnlib_path {property_path} --timeout {time}"
        
        self.execute(cmd, log_path, time, memory)

    def analyze(self):
        with open(self.verification_problem.paths["veri_log_path"], "r") as fp:
            lines = fp.readlines()
        veri_ans, veri_time = super().pre_analyze(lines)

        if not (veri_ans and veri_time):
            veri_ans = None
            veri_time = None
            for l in lines[-100:]:
                if "Result: " in l:
                    veri_ans = l.strip().split()[-1]
                elif "Time: " in l:
                    veri_time = float(l.strip().split()[-1])

                if veri_ans and veri_time:
                    break

        assert (
            veri_ans and veri_time
        ), f"Answer: {veri_ans}, time: {veri_time}, log: {self.verification_problem.paths['veri_log_path']}"
        
        return super().post_analyze(veri_ans, veri_time)
