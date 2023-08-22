import os

from .. import Verifier
from ..verifier_configs import VerifierConfigs


class Verinet(Verifier):
    def __init__(self, logger) -> None:
        super(Verinet, self).__init__(logger)
        self.__name__ = "verinet"
        self.logger = logger

        # TODO: fix this
        self.config_path = ""

    def configure(self):
        ...

    def run(self, model_path, property, log_path):
        # self.configure(property)
        artifact = property["artifact"]
        eps = property["eps"]
        img_id = property["id"]
        property_path = os.path.join(
            property["prop_dir"], f"{artifact}_{img_id}_{eps}.vnnlib"
        )
        time = property["time"]
        memory = property["memory"]

        # cmd = f"$SwarmHost/scripts/run_mnbab.sh --config $OCTOPUS/{self.config_path} --onnx_path $OCTOPUS/{model_path} --vnnlib_path $OCTOPUS/{property_path} --timeout {time}"

        cmd = f"$SwarmHost/scripts/run_verinet.sh $OCTOPUS/{model_path} $OCTOPUS/{property_path} {time} --input_shape 1 1 28 28"

        print(cmd)
        self.execute(cmd, log_path, time, memory)

    def analyze(self):
        ...
