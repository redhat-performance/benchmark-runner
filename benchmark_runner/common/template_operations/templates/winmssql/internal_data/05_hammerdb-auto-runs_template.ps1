cd c:\tools\hammerdb-4.12

mkdir results -ErrorAction SilentlyContinue

$tclBase = @'
#!/bin/tclsh

set tmpdir $::env(TMP)
puts "SETTING CONFIGURATION"
dbset db mssqls
dbset bm TPC-C

diset connection mssqls_tcp false
diset connection mssqls_port 1433
diset connection mssqls_azure false
diset connection mssqls_encrypt_connection true
diset connection mssqls_trust_server_cert true
diset connection mssqls_authentication windows
diset connection mssqls_server {(local)}
diset connection mssqls_linux_server {(localhost)}
diset connection mssqls_uid sa
diset connection mssqls_pass 100yard-
diset connection mssqls_linux_authent sql
diset connection mssqls_linux_odbc {ODBC Driver 18 for SQL Server}

diset tpcc mssqls_dbase tpcc
diset tpcc mssqls_driver timed
diset tpcc mssqls_total_iterations 10000000
diset tpcc mssqls_rampup {{ rampup }}
diset tpcc mssqls_duration {{ runtime }}
diset tpcc mssqls_checkpoint false
diset tpcc mssqls_timeprofile true
diset tpcc mssqls_allwarehouse true

loadscript
puts "TEST STARTED"
vuset vu VUCOUNT
vucreate
tcstart
tcstatus
set jobid [ vurun ]
vudestroy
tcstop
puts "TEST COMPLETE"
set of [ open $tmpdir/mssqls_tprocc w ]
puts $of $jobid
close $of
'@

$maxVU = {{ db_num_workers }}
$vuCounts = @()
$vu = {{ db_min_workers }}
while ($vu -le $maxVU) {
    $vuCounts += $vu
    $vu *= 2
}

for ($i=1; $i -le {{ iterations }}; $i++) {
    Write-Output "Iteration $i started"

    foreach ($vu in $vuCounts) {
        $vuPad = $vu.ToString().PadLeft(3, '0')
        $tclContent = $tclBase -replace 'VUCOUNT', $vu
        $tclFile = "mssqls_tprocc_auto_run${vuPad}.tcl"
        Set-Content -Path $tclFile -Value $tclContent

        .\hammerdbcli auto .\$tclFile > results\mssqls_tprocc_${vuPad}vu_run$i.out
        .\hammerdbcli auto .\scripts\tcl\mssqls\tprocc\mssqls_tprocc_result.tcl > results\mssqls_tprocc_${vuPad}vu_run$i.json
        Copy-Item -Path c:\Users\Administrator\AppData\Local\temp\hdbxtprofile.log -Destination results\mssqls_tprocc_${vuPad}vu-hdbxtprof_run$i.log
        Write-Output "$vu user run complete"
        Write-Output "+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-"
        Start-Sleep 15
    }

    Start-Sleep 30
}
