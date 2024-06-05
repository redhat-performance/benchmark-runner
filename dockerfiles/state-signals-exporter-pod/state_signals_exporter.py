
import state_signals
import argparse


class StateSignalsExporter:
    """
    This class runs state signals exporter
    """
    def __init__(self, redis_host: str, scale_num: int, timeout: int):
        self.__redis_host = redis_host
        self.__scale_num = scale_num
        self.__timeout = timeout

    def state_signals_exporter(self):
        """
        This method runs state_signals
        :return:
        """
        sig_ex = state_signals.SignalExporter(redis_host=self.__redis_host, process_name="benchmark-runner", conn_timeout=self.__timeout, log_level="DEBUG")
        print("\nBENCHMARK INIT\n")
        sig_ex.initialize_and_wait(
            await_sub_count=self.__scale_num, legal_events=["benchmark-start"], periodic=True, timeout=self.__timeout
        )
        print(f"Proof of response (subs): {str(sig_ex.subs)}")

        print("\nBENCHMARK START\n")
        result, _ = sig_ex.publish_signal(
            "benchmark-start", metadata={"something": "cool info"}, timeout=self.__timeout
        )
        print(f"SUBS CLEARED! Result code: {result}")

        print("\nBENCHMARK SHUTDOWN\n")
        print(f"Listening: {str(sig_ex.init_listener.is_alive())}")
        sig_ex.shutdown()
        print(f"Listening: {str(sig_ex.init_listener.is_alive())}")
        print("NO LONGER LISTENING, DONE")


def main():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Signal State Exporter')
    # Required positional argument
    parser.add_argument('redis_host', type=str,
                        help='Redis host')
    parser.add_argument('scale_num', type=int,
                        help='Number of scale workloads')
    parser.add_argument('timeout', type=int,
                        help='timeout')
    args = parser.parse_args()
    run = StateSignalsExporter(redis_host=args.redis_host, scale_num=args.scale_num, timeout=args.timeout)
    run.state_signals_exporter()


main()

# python3 /state_signals_exporter.py 'redis-deployment.redis-db.svc.cluster.local' 1 3600
