from ..verifiers.abcrown import ABCrown
from ..verifiers.mnbab import MNBab
from ..verifiers.verinet import Verinet
from ..verifiers.nnenum import NNEnum

from .property import LocalRobustnessProperty


class VerificationProblem:
    def __init__(
        self,
        logger,
        property,
        verifier,
        verifier_config,
        paths,
        greybox=False,
    ):
        self.logger = logger
        self.property = property
        self.paths = paths
        self.verifier_config = verifier_config
        self.init_verifiers(verifier)

    def init_verifiers(self, verifier):
        verifier_framework = verifier.split(":")[0]
        verifier_name = verifier.split(":")[1]

        if verifier_name == "abcrown":
            verifier = ABCrown(self)
        elif verifier_name == "abcrown2":
            verifier = ABCrown(self, beta=True)
        elif verifier_name == "mnbab":
            verifier = MNBab(self)
        elif verifier_name == "verinet":
            verifier = Verinet(self)
        elif verifier_name == "nnenum":
            verifier = NNEnum(self)
        elif verifier_name == "DNNV":
            assert verifier_framework == "DNNV"
            raise NotImplementedError()
        else:
            raise ValueError(verifier_name)
        self.verifier = verifier

    def generate_property(self):
        self.logger.info(f"Generating property ... ")
        if type(self.verifier) in [ABCrown, MNBab, Verinet, NNEnum]:
            assert self.property["type"] == "local robustness"
            self.property = LocalRobustnessProperty(self.logger, self.property)
            self.property.generate(self.paths["prop_dir"], format="vnnlib")
        else:
            raise NotImplementedError()
        self.logger.info(f"Property generated.")

    def verify(self):
        return self.verifier.run()

    def analyze(self):
        return self.verifier.analyze()
