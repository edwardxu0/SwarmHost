from .misc import cli
from .misc import logging
from .core.problem import VerificationProblem


def main():
    args = cli.parse_args()
    logger = logging.initialize(args)

    print(args)
    
    
    property_configs = {
        "format": args.property_format,
        "type": args.property_type,
        "artifact": args.artifact,
        "id": args.property_id,
        "eps": args.eps,
        "clip": args.p_clip,
        "mean": args.p_mean,
        'std': args.p_std
    }
    
    verifier_config = {
        "time": args.timeout,
        "memory": args.memory,
    }

    paths = {
        "model_path": args.onnx,
        "prop_dir": args.property_dir,
        "veri_config_path": args.veri_config_path,
        "veri_log_path": args.veri_log_path,
    }
    vp = VerificationProblem(
        logger,
        property_configs,
        args.verifier,
        verifier_config,
        paths,
    )

    match args.task:
        case "G":
            vp.generate_property(format=args.property_format)
        case "V":
            if args.property_path:
                vp.set_generic_property(args.property_path)
            else:
                vp.generate_property(format=args.property_format)

            vp.verify()
        case "A":
            a,t = vp.analyze()
            print(f'Result: {a}')
            print(f"Time: {t}")
            
        case _:
            pass


if __name__ == "__main__":
    main()
