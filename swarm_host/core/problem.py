from ..verifiers.abcrown import ABCrown
from ..verifiers.mnbab import MNBab
from .property import LocalRobustnessProperty


class VerificationProblem:
    def __init__(
        self,
        logger,
        veri_log_path,
        property,
        verifier,
        greybox=False,
    ):
        self.logger = logger
        self.veri_log_path = veri_log_path
        self.greybox = False
        self.property = property
        self.results = None
        self.init_verifiers(verifier)

    def init_verifiers(self, verifier):
        verifier_framework = verifier.split(":")[0]
        verifier_name = verifier.split(":")[1]

        if verifier_name == "abcrown":
            assert verifier_framework == "SH"
            verifier = ABCrown(self.logger)
        elif verifier_name == "mnbab":
            assert verifier_framework == "SH"
            verifier = MNBab(self.logger)
        elif verifier_name == 'verinet':
            v
        elif verifier_name == "DNNV":
            assert verifier_framework == "DNNV"
            raise NotImplementedError()
        else:
            raise ValueError(verifier_name)
        self.verifier = verifier

    def generate_property(self, property):
        self.logger.info(f"Generating property ... ")
        if isinstance(self.verifier, MNBab):
            assert property["type"] == "local robustness"
            self.property = LocalRobustnessProperty(property)
            self.property.generate(format="vnnlib")

        # no need for ABCrown
        elif isinstance(self.verifier, ABCrown):
            ...
        else:
            raise NotADirectoryError()
        self.logger.info(f"Property generated.  ")

    def verify(self, model_path, property):
        return self.verifier.run(model_path, property, self.veri_log_path)

    def analyze(self):
        return self.verifier.analyze(self.veri_log_path)
