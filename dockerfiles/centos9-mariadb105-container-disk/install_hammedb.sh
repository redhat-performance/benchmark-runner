https://hammerdb.com/download.html
curl -LO https://github.com/TPC-Council/HammerDB/releases/download/v4.0/HammerDB-4.0-Linux.tar.gz
tar -xf HammerDB-4.0-Linux.tar.gz
mkdir /hammer
mv HammerDB-4.0/* /hammer
export LD_LIBRARY=/hammer/lib:$LD_LIBRARY_PATH
dnf install -y tk
cd /hammer; ./bin/tclsh8.6
