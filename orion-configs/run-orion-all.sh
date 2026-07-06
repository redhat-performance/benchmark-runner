#!/bin/bash
# Run Orion regression detection for all PerfCI workloads
# Generates HTML visualizations into /opt/orion-reports/
# Usage: ./run-orion-all.sh [lookback_days]

set -euo pipefail

ES="http://localhost:9200"
REPORTS="/opt/orion-reports"
CONFIGS="$(cd "$(dirname "$0")" && pwd)"
LOOKBACK="${1:-90d}"
DATE=$(date +%Y-%m-%d)

declare -A INDEX_MAP=(
  [bootstorm]="bootstorm-results"
  [windows-bootstorm]="windows-results"
  [hammerdb]="hammerdb-results"
  [uperf]="uperf-results"
  [fio]="fio-results"
  [vdbench]="vdbench-results"
  [sysbench]="sysbench-results"
)

mkdir -p "$REPORTS"

FAILED=0
PASSED=0

for workload in "${!INDEX_MAP[@]}"; do
  index="${INDEX_MAP[$workload]}"
  config="$CONFIGS/perfci-${workload}.yaml"
  outdir="$REPORTS/$workload"
  mkdir -p "$outdir"

  echo "=== $workload ($index, lookback=$LOOKBACK) ==="

  if orion --es-server "$ES" \
       --metadata-index "$index" \
       --benchmark-index "$index" \
       --lookback "$LOOKBACK" \
       --hunter-analyze --viz \
       --save-output-path "$outdir/results.txt" \
       --config "$config" 2>&1; then
    echo "  -> OK: $outdir/"
    ((PASSED++))
  else
    echo "  -> FAILED: $workload"
    ((FAILED++))
  fi
  echo
done

echo "=== Done: $PASSED passed, $FAILED failed ==="
echo "Reports: http://$(hostname -f):9091/"
