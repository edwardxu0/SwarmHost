import os

from .. import Verifier


class NNEnum(Verifier):
    def __init__(self, verification_problem):
        super().__init__(verification_problem)
        self.__name__ = "NNEnum"

    def configure(self):
        ...

    def run(self):
        self.configure()

        property_path = self.verification_problem.property.property_path
        model_path = self.verification_problem.paths["model_path"]
        log_path = self.verification_problem.paths["veri_log_path"]

        time = self.verification_problem.verifier_config["time"]
        memory = self.verification_problem.verifier_config["memory"]

        cmd = f"$SwarmHost/scripts/run_nnenum.sh $OCTOPUS/{model_path} $OCTOPUS/{property_path} {time}"

        print(cmd)
        self.execute(cmd, log_path, time, memory)

    def analyze(self):
        with open(self.verification_problem.paths["veri_log_path"], "r") as fp:
            lines = fp.readlines()

        veri_ans, veri_time = super().pre_analyze(lines)

        if not (veri_ans and veri_time):
            for l in lines[-100:]:
                if "Result: network is SAFE" in l:
                    veri_ans = "unsat"
                elif "Result: network is UNSAFE with confirmed counterexample" in l:
                    veri_ans = "sat"

                if "Runtime:" in l:
                    if "(" not in l:
                        veri_time = float(l.split()[-2])
                    else:
                        veri_time = float(l[str.index(l, "(") + 1 :].split()[0])

                if "reached during execution" in l:
                    veri_ans = "timeout"
                    veri_time = float(l[str.index(l, "(") + 1 : str.index(l, ")")])

                error_pattern = [
                    "FloatingPointError: underflow encountered in multiply",
                    "underflow encountered in divide",
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
