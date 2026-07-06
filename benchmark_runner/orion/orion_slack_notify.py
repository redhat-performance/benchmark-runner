"""Post Orion regression results to Slack."""

import argparse
import json
import sys

from benchmark_runner.common.slack.slack_operations import SlackOperations


def build_message(results: list, run_date: str) -> str:
    regressions = [r for r in results if r['status'] == 'regression']
    msg = f"*PerfCI Orion Regression Report* ({run_date})\n\n"
    if regressions:
        msg += f":red_circle: *Regressions ({len(regressions)}/{len(results)}):*\n"
        for r in regressions:
            msg += f"  • *{r['name']}* (<{r['link']}|view report>)\n"
    else:
        msg += f":large_green_circle: *All {len(results)} workloads passed — no regressions*"
    return msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', required=True, help='JSON array of workload results')
    parser.add_argument('--date', required=True, help='Run date string')
    args = parser.parse_args()

    results = json.loads(args.results)
    msg = build_message(results, args.date)

    slack = SlackOperations()
    response = slack.post_message(msg)
    if not response.get('ok'):
        print(f"Slack notification failed: {response.get('error')}", file=sys.stderr)
        sys.exit(1)
    print("Slack notification sent")


if __name__ == '__main__':
    main()
