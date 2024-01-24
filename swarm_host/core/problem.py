from ..verifiers.abcrown import ABCrown
from ..verifiers.mnbab import MNBab
from ..verifiers.verinet import Verinet
from ..verifiers.nnenum import NNEnum
from ..verifiers.neuralsat import NeuralSat
from ..verifiers.veristable import VeriStable

from .property import Property, LocalRobustnessProperty


class VerificationProblem:
    def __init__(
        self,
        logger,
        property_configs,
        verifier,
        verifier_config,
        paths,
        greybox=False,
    ):
        self.logger = logger
        self.property_configs = property_configs
        self.paths = paths
        self.verifier_config = verifier_config
        self.init_verifiers(verifier)

    def init_verifiers(self, verifier):
        match verifier:
            case "acrown22":
                configs = {
                    'version': 22,
                    'beta': False,
                    'gpu': False
                }
                v = ABCrown(self, configs)
            case "abcrown":
                configs = {
                    'version': 22,
                    'beta': True,
                    'gpu': False
                }
                v = ABCrown(self, configs)
            case "abcrown22":
                configs = {
                    'version': 22,
                    'beta': True,
                    'gpu': False
                }
                v = ABCrown(self, configs)
            case "abcrown23":
                configs = {
                    'version': 23,
                    'beta': True,
                    'gpu': False
                }
                v = ABCrown(self, configs)
            case "abcrown23g":
                configs = {
                    'version': 23,
                    'beta': True,
                    'gpu': True
                }
                v = ABCrown(self, configs)
            case "mnbab":
                v = MNBab(self)
            case "verinet":
                v = Verinet(self)
            case "nnenum":
                v = NNEnum(self)
            case 'neuralsat':
                v = NeuralSat(self, version=1)
            case 'neuralsatp':
                v = NeuralSat(self, version=2)
            case 'neuralsatpp':
                v = NeuralSat(self, version=3)
            case 'veristable':
                v = VeriStable(self)
            case _:
                raise NotImplementedError(verifier)
        self.verifier = v

    def set_generic_property(self, path):
        self.logger.info(f"Using predefined generic property.")
        self.property = Property(self.logger)
        self.property.set(path)

    def generate_property(self, format="vnnlib", model_path=None):
        self.logger.info(f"Generating property ... ")
        
        if type(self.verifier) in [ABCrown, MNBab, Verinet, NNEnum, NeuralSat, VeriStable]:
            assert self.property_configs["type"] == "local robustness"
            self.property = LocalRobustnessProperty(self.logger, self.property_configs)
            self.property.generate(self.paths["prop_dir"], format=format, model_path=model_path)
        else:
            raise NotImplementedError()
        self.logger.info(f"Property generated.")

    def verify(self):
        config_path = self.paths["veri_config_path"]
        model_path = self.paths["model_path"]
        property_path = self.property.property_path
        log_path = self.paths["veri_log_path"]
        time = self.verifier_config["time"]
        memory = self.verifier_config["memory"]
        
        self.verifier.configure(config_path)
        
        return self.verifier.run(config_path, model_path, property_path, log_path, time, memory)

    def analyze(self):
        return self.verifier.analyze()
