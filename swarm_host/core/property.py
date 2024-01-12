import os
import onnxruntime as ort
import numpy as np
import onnx


import numpy
from torchvision import datasets, transforms
from pathlib import Path

class Property:
    def __init__(self, logger):
        self.logger = logger

    def set(self, path):
        self.property_path = path


class LocalRobustnessProperty(Property):
    def __init__(self, logger, property_configs):
        super().__init__(logger)
        self.property_configs = property_configs

    def generate(self, prop_dir, format, model_path=None):
        if format == "vnnlib":
            self.gen_vnnlib(prop_dir, model_path)
        else:
            raise NotImplementedError()

    def gen_vnnlib(self, prop_dir, model_path=None):
        artifact = self.property_configs["artifact"]
        eps = self.property_configs["eps"]
        img_id = self.property_configs["id"]
        Path(prop_dir).mkdir(exist_ok=True,parents=True)
        self.property_path = os.path.join(prop_dir, f"{artifact}_{img_id}_{eps}.vnnlib")

        t = [transforms.ToTensor()]
        
        mean = self.property_configs['mean']
        std = self.property_configs['std']
        if mean and std:
            t += [transforms.Normalize(mean, std)]
        elif not mean and not std:
            t += [transforms.Normalize((0,), (1,))]
        else:
            assert False,"mean and std must be configured the same time"
        transform = transforms.Compose(t)
        test_dataset = eval(f"datasets.{artifact}")(
            "data", download=True, train=False, transform=transform
        )
        img, label = test_dataset[img_id]
        img_npy = numpy.asarray(img)
        self.shape = img_npy.shape
        img_npy_flatten = img_npy.flatten()
        
        if self.property_configs["mrb"]:
            assert  model_path
            session = ort.InferenceSession(onnx.load(model_path).SerializeToString())
            #names = [i.name for i in sess.get_inputs()]
            #label= sess.run(None, dict(zip(names, img_npy)))
            session.get_modelmeta()
            
            input_names = [x.name for x in session.get_inputs()]
            output_names = [x.name for x in session.get_outputs()]
            
            assert len(input_names) == 1 and len(output_names) == 1
            if len(img_npy.shape) == 2:
                img_npy=img_npy.reshape(1,1,*(img_npy.shape))
            elif len(img_npy.shape) == 3:
                img_npy=img_npy.reshape(1,*(img_npy.shape))    
            elif len(img_npy.shape) == 4:
                pass
            else:
                raise NotImplementedError()
            
            print(img_npy.shape)
            #results = session.run([output_names[0]], {input_names[0]: img_npy})
            results = session.run(output_names, {input_names[0]:img_npy})

            pred = np.argmax(results)
            
            label=pred

        # generate VNN-lib Property
        # 1) define input
        vnn_lib_lines = [f"; {artifact} property with label: {label}.", ""]

        for x in range(len(img_npy_flatten)):
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
        for i, x in enumerate(img_npy_flatten):
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
        self.logger.debug(f"Property generated: {self.property_path}")