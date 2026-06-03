$hammerdb = "C:\tools\hammerdb-4.12"
$resultsPath = "$hammerdb\results"
$outputFile = "$resultsPath\hammerdb_result.json"

Write-Output "Parsing HammerDB results from $resultsPath"

$results = @{}

foreach ($outFile in (Get-ChildItem -Path $resultsPath -Filter "*.out" | Where-Object { $_.Name -match '_\d+vu_run\d+\.out$' })) {
    Write-Output "Analyzing: $($outFile.FullName)"

    if ($outFile.Name -match '_(\d+)vu_') {
        $workerCount = [int]$Matches[1]
    } else {
        Write-Output "WARNING: Cannot extract worker count from filename: $($outFile.Name)"
        continue
    }

    try {
        $text = [System.IO.File]::ReadAllText($outFile.FullName, [System.Text.Encoding]::Unicode)
        $tpmValues = [System.Collections.Generic.List[int]]::new()
        foreach ($line in ($text -split "`r?`n")) {
            if ($line -match '^(\d+)\s+MSSQLServer\s+tpm') {
                $val = [int]$Matches[1]
                if ($val -gt 0) { $tpmValues.Add($val) }
            }
        }

        if ($tpmValues.Count -gt 0) {
            $avgTpm = [int](($tpmValues | Measure-Object -Average).Average)
            if ($results.ContainsKey($workerCount)) {
                if ($avgTpm -gt $results[$workerCount]) { $results[$workerCount] = $avgTpm }
            } else {
                $results[$workerCount] = $avgTpm
            }
            Write-Output "  Worker $workerCount : avg TPM = $avgTpm (from $($tpmValues.Count) samples)"
        } else {
            Write-Output "WARNING: No TPM values found in $($outFile.Name)"
        }
    } catch {
        Write-Output "ERROR: Skipping file $($outFile.Name) -> $_"
    }
}

$sortedResults = @()
foreach ($key in ($results.Keys | Sort-Object)) {
    $sortedResults += [PSCustomObject]@{
        current_worker = $key
        tpm = $results[$key]
    }
}

$sortedResults | ConvertTo-Json -Depth 10 | Set-Content -Path $outputFile -Encoding UTF8
Write-Output "HammerDB results written to $outputFile"
Write-Output ($sortedResults | Format-Table -AutoSize | Out-String)
