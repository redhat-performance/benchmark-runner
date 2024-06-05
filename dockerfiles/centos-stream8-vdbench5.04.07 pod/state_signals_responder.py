
import sys
import state_signals
from multiprocessing import Process
import argparse
import subprocess


class StateSignalsResponder:
    """
    This class runs state signals responder
    """
    def __init__(self, redis_host: str, run_workload_method: str, timeout: int):
        self.__redis_host = redis_host
        self.__run_workload_method = run_workload_method
        self.__timeout = timeout

    def _listener(self):
        responder = state_signals.SignalResponder(
            redis_host=self.__redis_host, responder_name="benchmark-runner", conn_timeout=self.__timeout
        )
        for signal in responder.listen():
            if signal.tag == "bad":
                ras = 0
            elif signal.event == 'benchmark-start':
                output = subprocess.check_output(
                    self.__run_workload_method,
                    stderr=subprocess.STDOUT,
                    shell=True, timeout=self.__timeout,
                    universal_newlines=False)
                print(output.decode("utf-8"))
                if output:
                    ras = 1
                else:
                    ras = 0
            elif signal.event == 'shutdown':
                sys.exit()
            else:
                ras = 1
            # responder.respond(signal.publisher_id, signal.event, ras)
            responder.srespond(signal, ras=ras)


def main():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Signal State Responder')
    # Required positional argument
    parser.add_argument('redis_host', type=str,
                        help='Redis host')
    parser.add_argument('workload_method', type=str,
                        help='workload method')
    parser.add_argument('timeout', type=int,
                        help='timeout')
    args = parser.parse_args()
    run = StateSignalsResponder(redis_host=args.redis_host, run_workload_method=args.workload_method, timeout=args.timeout)
    init = Process(target=run._listener)
    init.start()

main()

# python3.9 /state_signals_responder.py redis-deployment.redis-db.svc.cluster.local /vdbench/vdbench_runner.sh 3600
