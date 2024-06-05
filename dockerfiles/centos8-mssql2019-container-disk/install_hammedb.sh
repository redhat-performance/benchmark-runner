https://hammerdb.com/download.html
curl -LO https://github.com/TPC-Council/HammerDB/releases/download/v4.0/HammerDB-4.0-Linux.tar.gz
tar -xf HammerDB-4.0-Linux.tar.gz
mkdir /hammer
mv HammerDB-4.0/* /hammer
export LD_LIBRARY=/hammer/lib:$LD_LIBRARY_PATH
dnf install -y tk
cd /hammer; ./bin/tclsh8.6

MSSQL ONLY
=========
[root@perf78 ~]# odbcinst -q -d -n "ODBC Driver 17 for SQL Server"
[root@perf78 ~]# vi /etc/odbcinst.ini
[root@perf78 ~]# [ODBC Driver 17 for SQL Server]
Description=Microsoft ODBC Driver 17 for SQL Server
Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1
UsageCount=1
