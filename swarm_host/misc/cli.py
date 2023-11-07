import argparse
from pyfiglet import Figlet


def parse_args():
    f = Figlet(font="slant")
    print(f.renderText("SwarmHost"), end="")

    parser = argparse.ArgumentParser(description="Spwarms Locusts", prog="SwarmHost")

    parser.add_argument(
        "task",
        type=str,
        choices=["G", "V"],
        help="Tasks to perform: [G]enerate property; [V]erify.",
    )
    parser.add_argument("--onnx", type=str, help="Onnx model path.")
    parser.add_argument(
        "--property_path",
        type=str,
        default=None,
        help="vnnlib property path; if not provided, vnnlib property will be generated by default with property_format, property_id and eps, etc.",
    )
    parser.add_argument(
        "--property_format",
        type=str,
        default="vnnlib",
        choices=["vnnlib"],
        help="Property format.",
    )
    parser.add_argument(
        "--property_type",
        type=str,
        default="local robustness",
        choices=["local robustness"],
        help="Property type.",
    )
    parser.add_argument(
        "--property_dir",
        type=str,
        help="Directory to store generated property.",
    )
    parser.add_argument(
        "--verifier", choices=["abcrown", "mnbab"], help="Verifier to execute."
    )

    parser.add_argument(
        "--veri_config_path",
        type=str,
        default=None,
        help="Path to store verifier configs.",
    )

    parser.add_argument(
        "--veri_log_path",
        type=str,
        default=None,
        help="Path to store verification log. Print to STDOUT if not set.",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=None,
        help="Timeout for verification.",
    )
    parser.add_argument(
        "-m",
        "--memory",
        type=str,
        default=None,
        help="Memory limit(Gb) for verification.",
    )

    parser.add_argument("--artifact", type=str, help="Artifact/dataset name.")

    parser.add_argument("--property_id", type=int, help="Property id.")
    parser.add_argument("--eps", type=float, help="Robustness radius(epsilon).")

    parser.add_argument("--debug", action="store_true", help="Print debug log.")
    parser.add_argument("--dumb", action="store_true", help="Silent mode.")

    return parser.parse_args()