cd C:\tools\fio

# Log file for monitoring
$logFile = "C:\tools\fio\run_fio_benchmark.log"

# Create results and data directories
New-Item -ItemType Directory -Force -Path results | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

# Parameters from template
$blockSizes = "{{ BLOCK_SIZES }}".Split(",")
$ioOperations = "{{ IO_OPERATION }}".Split(",")
$ioThreads = "{{ IO_THREADS }}".Split(",")
$ioDepths = "{{ IO_DEPTH }}".Split(",")
$duration = "{{ DURATION }}"
$size = "{{ SIZE }}"
$pause = {{ PAUSE }}

"FIO benchmark started at $(Get-Date)" | Tee-Object -FilePath $logFile

foreach ($bs in $blockSizes) {
    for ($j = 0; $j -lt $ioOperations.Length; $j++) {
        $op = $ioOperations[$j]
        $threads = if ($j -lt $ioThreads.Length) { $ioThreads[$j] } else { $ioThreads[0] }
        $depth = if ($j -lt $ioDepths.Length) { $ioDepths[$j] } else { $ioDepths[0] }
        $outputFile = "results\${bs}_${op}.json"

        "Running FIO: bs=$bs rw=$op numjobs=$threads iodepth=$depth duration=${duration}s" | Tee-Object -FilePath $logFile -Append

        $fioProcess = Start-Process -FilePath ".\fio.exe" -ArgumentList @(
            "--name=${bs}_${op}",
            "--ioengine=windowsaio",
            "--bs=$bs",
            "--rw=$op",
            "--numjobs=$threads",
            "--iodepth=$depth",
            "--size=$size",
            "--runtime=$duration",
            "--time_based",
            "--direct=1",
            "--thread",
            "--filename=data\fio_testfile",
            "--group_reporting",
            "--output-format=json",
            "--output=$outputFile"
        ) -Wait -PassThru -NoNewWindow -RedirectStandardError "results\${bs}_${op}_error.log"

        if ($fioProcess.ExitCode -ne 0) {
            "ERROR: FIO failed for bs=$bs rw=$op exit_code=$($fioProcess.ExitCode) at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
            $errorContent = Get-Content "results\${bs}_${op}_error.log" -Raw -ErrorAction SilentlyContinue
            if ($errorContent) { "  stderr: $errorContent" | Tee-Object -FilePath $logFile -Append }
        } else {
            "Completed: bs=$bs rw=$op at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
        }
        Start-Sleep -Seconds $pause
    }
}

# Parse results and generate summary
"Parsing results..." | Tee-Object -FilePath $logFile -Append
powershell -NoProfile -ExecutionPolicy Bypass -File C:\tools\fio\parse_fio_results.ps1
"FIO benchmark completed at $(Get-Date)" | Tee-Object -FilePath $logFile -Append
