wget https://cloud.centos.org/centos/8-stream/x86_64/images/CentOS-Stream-GenericCloud-8-20210603.0.x86_64.qcow2
# run inside the container disk
sudo dnf -y update
dnf install -y epel-release
dnf install -y python3-pip
dnf install -y git redis wget

git clone https://github.com/bbenshab/vdpod
cd vdpod/
mkdir /vdbench
# copying vdbench
cp vdbench50407.zip /vdbench/vdbench50407.zip
cp vdbench_runner.sh /vdbench/vdbench_runner.sh

# installing java
yum -y install java

# installing vim
yum -y install vim

# installing monitoring tools
yum -y install procps
yum -y install sysstat

NTFS=ntfs3g
cp -r ${NTFS}  /${NTFS}
cd /ntfs3g/
yum -y install xfsprogs
yum -y groupinstall "Development Tools"
tar -xvf ntfs-3g_ntfsprogs-2017.3.23.tgz --strip-components 1
./configure --prefix=/usr/local --disable-static
make
make install
rm -rf /ntfs3g

# extracting vdbench files
unzip /vdbench/vdbench50407.zip -d /vdbench/
chmod +x /vdbench/vdbench

# add-on for state-signals
dnf install -y python3.9
cd /
python3.9 -m pip --no-cache-dir install --upgrade pip && pip3.9 --no-cache-dir install state-signals==0.5.2
cp state_signals_responder.py /state_signals_responder.py