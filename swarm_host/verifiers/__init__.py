import os
import sys
import subprocess

from abc import ABC

RES_MONITOR_PRETIME = 60


class Verifier(ABC):
    def __init__(self, logger):
        self.logger = logger

    def execute(self, cmd, log_path, time, memory):
        res_monitor_path = os.path.join(os.environ["DNNV"], "tools", "resmonitor.py")
        cmd = (
            f"python3 {res_monitor_path} -T {time+RES_MONITOR_PRETIME} -M {memory} "
            + cmd
        )

        save_log = True
        if save_log:
            veri_log_file = open(log_path, "w")
        else:
            veri_log_file = sys.stdout

        self.logger.info("Executing DNNV ...")
        self.logger.debug(cmd)
        self.logger.debug(f"Verification output path: {veri_log_file}")

        """
        # Run verification twice to account for performance issues
        # TODO: fix later
        self.logger.info("Dry run ...")
        if save_log:
            open(self.veri_log_path, "a").write("********Dry_Run********\n")
        else:
            print("********Dry_Run********\n")
        sp = subprocess.Popen(
            cmd, shell=True, stdout=veri_log_file, stderr=veri_log_file
        )
        rc = sp.wait()
        assert rc == 0
        """

        self.logger.info("Wet run ...")
        if save_log:
            with open(log_path, "a") as fp:
                fp.write("********Wet_Run********\n")
        else:
            print("********Wet_Run********\n")
        # 2. Wet run
        sp = subprocess.Popen(
            cmd, shell=True, stdout=veri_log_file, stderr=veri_log_file
        )
        rc = sp.wait()
        assert rc == 0
        veri_log_file.close()
