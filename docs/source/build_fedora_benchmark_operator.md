# Build Fedora for benchmark-operator

## Download Fedora VM

### Install the following

```bash
dnf -y update
dnf install -y python3-pip git redis wget podman
dnf -y install @virt
sudo dnf install -y /usr/bin/virt-customize
dnf install -y qemu-kvm libvirt libguestfs-tools virt-install virt-top
systemctl enable --now libvirtd
```

### Download qcow2 Fedora image

https://fedoraproject.org/cloud/download/

## Update password using guestfish for qcow2 (pass: fedora)

```bash
sudo guestfish --rw -a Fedora-Cloud-Base-Generic-43-1.6.x86_64.qcow2
run
list-filesystems
# Find the one with root
mount /dev/sda5 /
ls /
```

Create password hash (run in Linux terminal):

```bash
openssl passwd -1 fedora
```

In guestfish, edit shadow:

```bash
vi /root/etc/shadow
# Change user root line to use the hash, e.g.:
# root:$1$3hZtZC4X$.oTYM300EkNra8pqYh3T.1::0:99999:7:::
```

Edit SSH config to allow root login:

```bash
vi /root/etc/ssh/sshd_config
# Set: PermitRootLogin yes
exit
```

## Run Fedora VM

```bash
virt-install --name fedora43 --memory 16384 --vcpus 4 --disk Fedora-Cloud-Base-Generic-43-1.6.x86_64.qcow2 --import --os-variant fedora41
```

## Connect to Fedora VM

```bash
virsh net-dhcp-leases default
ssh root@192.168.122.114
```

### Add user fedora

```bash
sudo useradd -m fedora
sudo passwd fedora
```

## Install Python 3.11.2 inside Fedora VM

Benchmark-operator requires Python 3.11.2. The following instructions explain how to install it on a fresh Fedora VM.

### 1. Install required system packages

These are needed to build Python from source:

```bash
sudo dnf update -y
sudo dnf install -y \
    gcc make patch bzip2 bzip2-devel zlib-devel \
    xz-devel libffi-devel readline-devel sqlite-devel \
    openssl-devel wget curl python3-pip python3.11-setuptools git redis podman
```

### 2. Install pyenv

Install pyenv for your current user:

```bash
curl https://pyenv.run | bash
```

### 3. Configure your shell

Add the following to `~/.bashrc` (or `~/.bash_profile` for login shells):

```bash
# pyenv setup
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"       # for login shells
eval "$(pyenv init -)"            # for interactive shells
eval "$(pyenv virtualenv-init -)" # optional if using pyenv-virtualenv
```

Reload your shell:

```bash
source ~/.bashrc
```

Check pyenv is working:

```bash
pyenv --version
```

### 4. Install Python 3.11.2

Install the desired Python version:

```bash
pyenv install 3.11.2
```

Check the installed versions:

```bash
pyenv versions
```

### 5. Set Python 3.11.2 as global

Make Python 3.11.2 your default for the user:

```bash
pyenv global 3.11.2
```

Verify:

```bash
python --version
# should show Python 3.11.2
which python
# should show ~/.pyenv/shims/python
```

### Use a specific Python version in a project folder

```bash
cd /path/to/project
pyenv local 3.11.2
python --version  # Python 3.11.2 only in this folder
```

Set default python for application:

```bash
sudo alternatives --install /usr/bin/python python /usr/bin/python3.14 10
sudo alternatives --install /usr/bin/python python /root/.pyenv/versions/3.11.2/bin/python 20
sudo alternatives --config python
```

### Install Python 3.11.2 from source (altinstall)

```bash
# Install build dependencies
sudo dnf groupinstall "Development Tools" -y
sudo dnf install gcc bzip2 bzip2-devel libffi-devel zlib-devel xz-devel wget make -y

# Download Python 3.11.2
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.2/Python-3.11.2.tgz
sudo tar xzf Python-3.11.2.tgz
cd Python-3.11.2

# Build and install in /usr/local
sudo ./configure --enable-optimizations --prefix=/usr/local
sudo make -j$(nproc)
sudo make altinstall  # altinstall avoids overwriting system python3
```

## Install benchmark-wrapper and verify

```bash
pip install git+https://github.com/cloud-bulldozer/benchmark-wrapper
```

Verify:

```bash
run_snafu
```

Expected output:

```
usage: run_snafu [-v] [--config CONFIG] -t TOOL [--run-id [RUN_ID]] [--archive-file ARCHIVE_FILE] [--create-archive]
run_snafu: error: the following arguments are required: -t/--tool
```

Seeing this message confirms the installation succeeded.

## Build container disk

### Create Dockerfile

```bash
cat > Dockerfile << 'EOF'
FROM registry.access.redhat.com/ubi8/ubi:latest AS builder
ADD --chown=107:107 Fedora-Cloud-Base-Generic-43-1.6.x86_64.qcow2 /disk/
RUN chmod 0440 /disk/*

FROM scratch
COPY --from=builder /disk/* /disk/
EOF
```

### Build and push the updated qcow2 image

```bash
podman build -t quay.io/benchmark-runner/fedora-container-disks:43 . --no-cache
podman push quay.io/benchmark-runner/fedora-container-disks:43
```

## Stop / destroy KVM

```bash
virsh list --all
# stop
virsh destroy fedora43
# shutdown / start
virsh shutdown fedora43
virsh start fedora43
# delete
virsh undefine fedora43 --remove-all-storage
```
