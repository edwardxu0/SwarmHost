import os

import numpy
from torchvision import datasets, transforms


class Property:
    def __init__(self, logger):
        self.logger = logger

    def generate(self):
        ...


class LocalRobustnessProperty(Property):
    def __init__(self, logger, property_configs):
        super().__init__(logger)
        self.property_configs = property_configs

    def generate(self, prop_dir, format):
        if format == "vnnlib":
            self.gen_vnnlib(prop_dir)
        else:
            raise NotImplementedError()

    def gen_vnnlib(self, prop_dir):
        artifact = self.property_configs["artifact"]
        eps = self.property_configs["eps"]
        img_id = self.property_configs["id"]
        self.property_path = os.path.join(prop_dir, f"{artifact}_{img_id}_{eps}.vnnlib")

        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0,), (1,))]
        )
        test_dataset = eval(f"datasets.{artifact}")(
            "data", download=True, train=False, transform=transform
        )
        img, label = test_dataset[img_id]
        img_npy = numpy.asarray(img).flatten()

        # generate VNN-lib Property
        # 1) define input
        vnn_lib_lines = [f"; {artifact} property with label: {label}.", ""]

        for x in range(len(img_npy)):
            vnn_lib_lines += [f"(declare-const X_{x} Real)"]

        # 2) define output
        vnn_lib_lines += [""]
        if artifact in ["MNIST", "CIFAR10"]:
            nb_output = 10
        elif artifact == "DAVE2":
            nb_output = 1
        else:
            assert False
        for x in range(nb_output):
            vnn_lib_lines += [f"(declare-const Y_{x} Real)"]

        # 3) define input constraints:
        vnn_lib_lines += ["", "; Input constraints:"]
        for i, x in enumerate(img_npy):
            lb = x - eps
            ub = x + eps
            if "clip" in self.property_configs and self.property_configs["clip"]:
                if lb < 0:
                    lb = 0.0
                if ub > 1:
                    ub = 1.0
            vnn_lib_lines += [
                f"(assert (<= X_{i} {ub}))",
                f"(assert (>= X_{i} {lb}))",
            ]

        # 4) define output constraints:
        vnn_lib_lines += ["", f"; Output constraints:"]
        if artifact in ["MNIST", "CIFAR10"]:
            vnn_lib_lines += ["(assert (or"]
            for x in range(nb_output):
                if not x == label:
                    vnn_lib_lines += [f"    (and (>= Y_{x} Y_{label}))"]
            vnn_lib_lines += ["))"]

        elif artifact == "DAVE2":
            assert False
            lines = open(
                os.path.join(os.path.dirname(img_path), "properties.csv"), "r"
            ).readlines()

            for x in lines[1:]:
                tokens = x.split(",")
                if img_id == int(tokens[0]):
                    min_val = tokens[-2]
                    max_val = tokens[-1]
                    break
            assert min_val and max_val
            vnn_lib_lines += ["(assert (or"]
            vnn_lib_lines += [f"(and (>= Y_0 {min_val}))"]
            vnn_lib_lines += [f"(and (<= Y_0 {max_val})"]
            vnn_lib_lines += ["))"]
        else:
            assert False

        with open(self.property_path, "w") as fp:
            fp.writelines(x + "\n" for x in vnn_lib_lines)
        self.logger.debug("Property generated: {self.property_path}")
