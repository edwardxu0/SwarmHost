import os

from .. import Verifier
from ..verifier_configs import VerifierConfigs


class MNBab(Verifier):
    def __init__(self, verification_problem):
        super().__init__(verification_problem)
        self.__name__ = "mn-bab"

    def configure(self):
        vc = VerifierConfigs(self)
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

        cmd = f"$SwarmHost/scripts/run_mnbab.sh --config $OCTOPUS/{config_path} --onnx_path $OCTOPUS/{model_path} --vnnlib_path $OCTOPUS/{property_path} --timeout {time}"

        print(cmd)
        self.execute(cmd, log_path, time, memory)

    def analyze(self):
        with open(self.verification_problem.paths["veri_log_path"], "r") as fp:
            lines = fp.readlines()

        veri_ans, veri_time = super().pre_analyze(lines)

        if not (veri_ans and veri_time):
            veri_ans = None
            veri_time = None
            for l in lines[-100:]:
                if "Result: True" in l:
                    veri_ans = "unsat"
                elif "Result: False" in l:
                    veri_ans = "sat"

                if "Time:" in l:
                    veri_time = float(l.split()[-1][:-1])

                error_pattern = [
                    "index_of_last_intermediate_bounds_kept",
                    "cannot reshape tensor of 0 elements into shape",
                    "Model was converted incorrectly",
                    "RuntimeError: mat1 and mat2 shapes cannot be multiplied",
                ]
                if any([True for x in error_pattern if x in l]):
                    veri_ans = "error"
                    veri_time = -1

                if veri_ans and veri_time:
                    break

        assert (
            veri_ans and veri_time
        ), f"Answer: {veri_ans}, time: {veri_time}, log: {self.verification_problem.paths['veri_log_path']}"
        return veri_ans, veri_time
