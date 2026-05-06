# --- Setup ---
$hammerdb = "C:\tools\hammerdb-4.12"
$logFile = "$hammerdb\run_hammerdb_benchmark.log"
$resultsFolder = "$hammerdb\results"

# Clear the log file at the beginning of each run
Clear-Content -Path $logFile -ErrorAction SilentlyContinue

# Remove old results
if (Test-Path $resultsFolder) {
    Remove-Item -Path "$resultsFolder\*" -Recurse -Force -ErrorAction SilentlyContinue
}

function Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $message"
    Write-Host $logMessage
    $logMessage | Add-Content $logFile
}

# --- Start Script ---
Log "Benchmark script started"

Log "Changed directory to $hammerdb"
cd $hammerdb

Log "05 Running HammerDB automation script - 05_hammerdb-auto-runs.ps1"
.\05_hammerdb-auto-runs.ps1 2>&1 | ForEach-Object { Log $_ }
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: HammerDB automation script failed with exit code $LASTEXITCODE"
    exit 1
}

Log "06 Parsing HammerDB results - 06_parse_results.ps1"
.\06_parse_results.ps1 2>&1 | ForEach-Object { Log $_ }
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: HammerDB results parsing failed with exit code $LASTEXITCODE"
    exit 1
}

Log "Benchmark script finished"
