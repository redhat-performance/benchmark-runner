https://hammerdb.com/download.html
curl -LO https://github.com/TPC-Council/HammerDB/releases/download/v4.12/HammerDB-4.12-Linux.tar.gz
tar -xf HammerDB-4.12-Linux.tar.gz
mkdir -p /hammer
mv HammerDB-4.12/* /hammer
export LD_LIBRARY_PATH=/hammer/lib:$LD_LIBRARY_PATH
dnf install -y tk
rm -rf /root/HammerDB*
cd /hammer; ./bin/tclsh8.6
Verified:
puts "Hello World!"
