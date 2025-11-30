https://hammerdb.com/download.html
curl -LO https://github.com/TPC-Council/HammerDB/releases/download/v4.0/HammerDB-4.0-Linux.tar.gz
tar -xf HammerDB-4.0-Linux.tar.gz
mkdir /hammer
mv HammerDB-4.0/* /hammer
export LD_LIBRARY=/hammer/lib:$LD_LIBRARY_PATH
dnf install -y tk
cd /hammer; ./bin/tclsh8.6

Change postgres password (can be configured in the run script)
=======================
vi /hammer/config/mssqlserver.xml
<mssqls_pass>s3curePasswordString</mssqls_pass>
vi /hammer/config/postgresql.xml
<pg_user>POSTGRES</pg_user>
<pg_pass>s3curePasswordString</pg_pass>
