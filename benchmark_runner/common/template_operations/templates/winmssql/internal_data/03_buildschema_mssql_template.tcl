#!/bin/tclsh

global complete
proc wait_to_complete {} {
    global complete
    set complete [vucomplete]
    if {!$complete} { after 5000 wait_to_complete } else { exit }
}

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
diset connection mssqls_pass s3curePasswordString
diset connection mssqls_linux_authent sql
diset connection mssqls_linux_odbc {ODBC Driver 18 for SQL Server}

diset tpcc mssqls_count_ware {{ db_warehouses }}
diset tpcc mssqls_num_vu {{ db_num_workers }}
diset tpcc mssqls_dbase tpcc
diset tpcc mssqls_imdb false
diset tpcc mssqls_bucket 1
diset tpcc mssqls_durability SCHEMA_AND_DATA
diset tpcc mssqls_checkpoint false

puts "SCHEMA BUILD STARTED"
buildschema
wait_to_complete
vwait forever
