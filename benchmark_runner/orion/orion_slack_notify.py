"""Post Orion regression results to Slack."""

import argparse
import json
import sys

from benchmark_runner.common.slack.slack_operations import SlackOperations


def build_message(results: list, run_date: str) -> str:
    regressions = [r for r in results if r['status'] == 'regression']
    timeouts = [r for r in results if r['status'] == 'timeout']
    msg = f"*PerfCI Orion Regression Report* ({run_date})\n\n"
    if regressions:
        msg += f":red_circle: *Regressions ({len(regressions)}/{len(results)}):*\n"
        for r in regressions:
            msg += f"  • *{r['name']}* (<{r['link']}|view report>)\n"
    if timeouts:
        msg += f":warning: *Timed out ({len(timeouts)}):* {', '.join(r['name'] for r in timeouts)}\n"
    if not regressions and not timeouts:
        msg += f":large_green_circle: *All {len(results)} workloads passed — no regressions*"
    return msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', help='JSON array of workload results')
    parser.add_argument('--results-file', help='Path to JSON file with workload results')
    parser.add_argument('--date', required=True, help='Run date string')
    args = parser.parse_args()

    if args.results_file:
        with open(args.results_file) as f:
            results = json.load(f)
    elif args.results:
        results = json.loads(args.results)
    else:
        print("Either --results or --results-file is required", file=sys.stderr)
        sys.exit(1)
    msg = build_message(results, args.date)

    slack = SlackOperations()
    response = slack.post_message(msg)
    if not response.get('ok'):
        print(f"Slack notification failed: {response.get('error')}", file=sys.stderr)
        sys.exit(1)
    print("Slack notification sent")


if __name__ == '__main__':
    main()
