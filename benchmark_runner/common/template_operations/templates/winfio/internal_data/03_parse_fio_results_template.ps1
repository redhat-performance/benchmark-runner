cd C:\tools\fio

$summary = @{}

Get-ChildItem -Path results -Filter *.json | ForEach-Object {
    if ($_.Name -eq "fio_summary.json") { return }

    $data = Get-Content $_.FullName -Raw | ConvertFrom-Json

    foreach ($job in $data.jobs) {
        $bs = $job.'job options'.bs
        $rw = $job.'job options'.rw

        if ($rw -in @("read", "randread")) {
            $ioData = $job.read
        } else {
            $ioData = $job.write
        }

        $latNs = $ioData.lat_ns
        $p99 = 0
        if ($latNs.percentile -and $latNs.percentile.'99.000000') {
            $p99 = [math]::Round($latNs.percentile.'99.000000' / 1000, 2)
        }

        if (-not $summary.ContainsKey($bs)) {
            $summary[$bs] = @{}
        }

        $summary[$bs][$rw] = @{
            TotalIOPS = [math]::Round($ioData.iops, 2)
            TotalBW_KBs = [math]::Round($ioData.bw, 2)
            LatAvg_usec = [math]::Round($latNs.mean / 1000, 2)
            LatP99_usec = $p99
        }
    }
}

$summary | ConvertTo-Json -Depth 4 | Set-Content -Path results\fio_summary.json
Write-Output "FIO summary saved to results\fio_summary.json"
Get-Content results\fio_summary.json
