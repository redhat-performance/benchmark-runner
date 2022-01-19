wget https://cloud.centos.org/centos/8-stream/x86_64/images/CentOS-Stream-GenericCloud-8-20210603.0.x86_64.qcow2
# run inside the container disk
sudo dnf -y update
dnf install -y epel-release
dnf install -y python3-pip
dnf install -y git redis wget
git clone https://github.com/bbenshab/vdpod
cd vdpod/
mkdir /vdbench
cp -r vdbench_linux/*  /vdbench
cp vdbench_runner.sh /vdbench/vdbench_runner.sh
yum -y install java
yum -y install vim
NTFS=ntfs3g
cp -r ${NTFS}  /${NTFS}
cd /ntfs3g/
yum -y install xfsprogs
yum -y groupinstall "Development Tools"
tar -xvf ntfs-3g_ntfsprogs-2017.3.23.tgz --strip-components 1
./configure --prefix=/usr/local --disable-static
make
rm -rf /ntfs3g