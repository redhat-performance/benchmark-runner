# --- Setup ---
$hammerdb = "C:\tools\hammerdb-4.12"
$mssql = "D:\mssql"
$logFile = "$hammerdb\run_prepare_hammerdb.log"

# Clear the log file at the beginning of each run
Clear-Content -Path $logFile -ErrorAction SilentlyContinue

function Log {
    param([string]$message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - $message"
    Write-Host $logMessage
    $logMessage | Add-Content $logFile
}

# --- Start Script ---
Log "Prepare script started"

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

Log "Prepare script finished"
