$hammerdb = "C:\tools\hammerdb-4.12"
$resultsPath = "$hammerdb\results"
$outputFile = "$resultsPath\hammerdb_result.json"

Write-Output "Parsing HammerDB results from $resultsPath"

$results = @{}

foreach ($jsonFile in (Get-ChildItem -Path $resultsPath -Filter "*.json" | Where-Object { $_.Name -match '_\d+vu_run\d+\.json$' })) {
    Write-Output "Analyzing: $($jsonFile.FullName)"

    if ($jsonFile.Name -match '_(\d+)vu_') {
        $workerCount = [int]$Matches[1]
    } else {
        Write-Output "WARNING: Cannot extract worker ID from filename: $($jsonFile.Name)"
        continue
    }

    try {
        $text = [System.IO.File]::ReadAllText($jsonFile.FullName, [System.Text.Encoding]::Unicode)
        $text = $text -replace "`r`n", "`n" -replace "`r", "`n"

        if ($text -match '(?s)\{"MSSQLServer tpm":\s*\{.*?\}\s*\}') {
            $jsonBlock = $Matches[0]
            $tpmData = $jsonBlock | ConvertFrom-Json
            # Filter out 0 values (ramp-up period) before averaging
            $tpmValues = $tpmData.'MSSQLServer tpm'.PSObject.Properties | ForEach-Object { [int]$_.Value } | Where-Object { $_ -gt 0 }
            $avgTpm = [int](($tpmValues | Measure-Object -Average).Average)

            if ($results.ContainsKey($workerCount)) {
                if ($avgTpm -gt $results[$workerCount]) {
                    $results[$workerCount] = $avgTpm
                }
            } else {
                $results[$workerCount] = $avgTpm
            }
            Write-Output "  Worker $workerCount : avg TPM = $avgTpm"
        } else {
            Write-Output "WARNING: Could not find MSSQLServer tpm block in $($jsonFile.Name)"
        }
    } catch {
        Write-Output "ERROR: Skipping file $($jsonFile.Name) -> $_"
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
