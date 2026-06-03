cd C:\tools\fio

# Log file for monitoring
$logFile = "C:\tools\fio\run_fio_benchmark.log"

# Create results directory
New-Item -ItemType Directory -Force -Path results | Out-Null

# Ensure FIO target directory exists on D: and set working path
New-Item -ItemType Directory -Force -Path "D:\fio" | Out-Null

# Parameters from template
$blockSizes = "{{ BLOCK_SIZES }}".Split(",")
$ioOperations = "{{ IO_OPERATION }}".Split(",")
$ioThreads = "{{ IO_THREADS }}".Split(",")
$ioDepths = "{{ IO_DEPTH }}".Split(",")
$duration = "{{ DURATION }}"
$size = "{{ SIZE }}"
$pause = {{ PAUSE }}

# Change working directory to D:\fio so FIO creates test files there
Set-Location D:\fio
"FIO working directory: $(Get-Location)" | Tee-Object -FilePath $logFile -Append
"FIO benchmark started at $(Get-Date)" | Tee-Object -FilePath $logFile -Append

foreach ($bs in $blockSizes) {
    for ($j = 0; $j -lt $ioOperations.Length; $j++) {
        $op = $ioOperations[$j]
        $threads = if ($j -lt $ioThreads.Length) { $ioThreads[$j] } else { $ioThreads[0] }
        $depth = if ($j -lt $ioDepths.Length) { $ioDepths[$j] } else { $ioDepths[0] }
        $outputFile = "C:\tools\fio\results\${bs}_${op}.json"

        "Running FIO: bs=$bs rw=$op numjobs=$threads iodepth=$depth duration=${duration}s" | Tee-Object -FilePath $logFile -Append

        & "C:\tools\fio\fio.exe" `
            "--name=${bs}_${op}" `
            "--ioengine=windowsaio" `
            "--bs=$bs" `
            "--rw=$op" `
            "--numjobs=$threads" `
            "--iodepth=$depth" `
            "--size=$size" `
            "--runtime=$duration" `
            "--time_based" `
            "--direct=1" `
            "--thread" `
            "--directory=D:\fio" `
            "--group_reporting" `
            "--output-format=json" `
            "--output=$outputFile" 2>"C:\tools\fio\results\${bs}_${op}_error.log"

        if ($LASTEXITCODE -ne 0) {
            "ERROR: FIO failed for bs=$bs rw=$op exit_code=$LASTEXITCODE at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
            $errorContent = Get-Content "C:\tools\fio\results\${bs}_${op}_error.log" -Raw -ErrorAction SilentlyContinue
            if ($errorContent) { "  stderr: $errorContent" | Tee-Object -FilePath $logFile -Append }
        } else {
            "Completed: bs=$bs rw=$op at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
        }
        Start-Sleep -Seconds $pause
    }
}

# Parse results and generate summary
"Parsing results..." | Tee-Object -FilePath $logFile -Append
powershell -NoProfile -ExecutionPolicy Bypass -File C:\tools\fio\03_parse_fio_results.ps1
"FIO benchmark completed at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
