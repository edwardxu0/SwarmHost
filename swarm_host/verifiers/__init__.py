import os
import sys
import subprocess


class Verifier:
    def __init__(self, verification_problem):
        self.verification_problem = verification_problem
        self.logger = verification_problem.logger
        self.RES_MONITOR_PRETIME = 200

    def execute(self, cmd, log_path, time, memory):
        res_monitor_path = os.path.join(os.environ["SwarmHost"], "lib", "resmonitor.py")
        cmd = (
            f"python3 {res_monitor_path} -T {time+self.RES_MONITOR_PRETIME} -M {memory} "
            + cmd
        )

        if log_path:
            veri_log_fp = open(log_path, "w")
        else:
            veri_log_fp = sys.stdout

        self.logger.info("Executing verification ...")
        self.logger.debug(cmd)
        self.logger.debug(f"Verification output path: {veri_log_fp}")

        sp = subprocess.Popen(cmd, shell=True, stdout=veri_log_fp, stderr=veri_log_fp)
        rc = sp.wait()
        assert rc == 0
        if log_path:
            veri_log_fp.close()

    def pre_analyze(self, lines):
        veri_ans = None
        veri_time = None

        for l in lines:
            if "Timeout (terminating process)" in l:
                veri_ans = "timeout"
                veri_time = float(l.strip().split()[-1])
            elif "Out of Memory" in l:
                veri_ans = "memout"
                veri_time = float(l.strip().split()[-1])

        return veri_ans, veri_time

    def post_analyze(self, answer, time):
        if answer != 'timeout' and time > self.verification_problem.verifier_config["time"]:
            answer = 'timeout'
            time = self.verification_problem.verifier_config["time"]
        return answer, time