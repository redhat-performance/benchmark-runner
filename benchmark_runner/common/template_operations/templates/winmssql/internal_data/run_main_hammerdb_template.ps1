# --- Setup ---
$hammerdb = "C:\tools\hammerdb-4.12"
$mssql = "D:\mssql"
$logFile = "$hammerdb\run_main_hammerdb.log"
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
    Write-Host $logMessage                  # Console output
    $logMessage | Add-Content $logFile      # Append to log file
}

# --- Start Script ---
Log "Script started"

Log "Changed directory to $hammerdb"
cd $hammerdb

Log "Starting MSSQL service"
start-service -name mssqlserver

Log "01 Provisioning data disk - 01_provision-data-disk.ps1"
.\01_provision-data-disk.ps1 -DiskID 1
if ($LASTEXITCODE -ne 0) {
    Log "ERROR: Disk provisioning failed"
    exit 1
}

Log "Creating directories"
mkdir $mssql -ErrorAction SilentlyContinue
mkdir $mssql\data -ErrorAction SilentlyContinue

Log "Restarting MSSQL service"
restart-service -name mssqlserver
$svc = Get-Service -Name mssqlserver
Log "MSSQL service status: $($svc.Status)"
if ($svc.Status -ne 'Running') {
    Log "ERROR: MSSQL service is not running"
    exit 1
}

Log "Starting HammerDB Windows Service"
Start-Process powershell.exe -ArgumentList "-NoExit -Command & {$hammerdb\hammerdbws}"

Log "02 Creating database using SQL script - 02_create_db.sql"
sqlcmd -U sa -P 100yard- -i 02_create_db.sql

Log "03 Building schema using HammerDB CLI - 03_buildschema_mssql.tcl"
.\hammerdbcli auto .\scripts\tcl\mssqls\tprocc\03_buildschema_mssql.tcl

Log "04 Applying SQL trace flags - 04_traceflags.sql"
sqlcmd -E -i 04_traceflags.sql

Log "Sleeping for 60 seconds to let services stabilize"
Start-Sleep 60

Log "05 Running HammerDB automation script - 05_hammerdb-auto-runs.ps1"
.\05_hammerdb-auto-runs.ps1 2>&1 | ForEach-Object { Log $_ }

Log "06 Parsing HammerDB results - 06_parse_results.ps1"
.\06_parse_results.ps1 2>&1 | ForEach-Object { Log $_ }

Log "Script finished"
