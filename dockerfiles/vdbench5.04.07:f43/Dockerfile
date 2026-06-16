FROM quay.io/fedora/fedora:43
# copying vdbench
COPY vdbench50407.zip  /vdbench/vdbench50407.zip
COPY vdbench_runner.sh /vdbench/vdbench_runner.sh

# Install Java 21 (OpenJDK) - only Java 21+ available on CentOS Stream 10
RUN dnf -y install java-21-openjdk java-21-openjdk-devel

# installing vim
RUN dnf -y install vim

# installing monitoring tools
RUN dnf -y install procps
RUN dnf -y install sysstat

# add ntfs & xfs support
ENV NTFS=ntfs3g
COPY ${NTFS}  /${NTFS}
WORKDIR ${NTFS}
RUN dnf -y install xfsprogs
RUN dnf -y install gcc gcc-c++ make automake autoconf libtool fuse-devel \
    && tar -xvf ntfs-3g_ntfsprogs-2017.3.23.tgz --strip-components 1 \
    && ./configure --prefix=/usr/local --disable-static \
    && make \
    && make install

#delete installation files
WORKDIR /root
RUN rm -rf /ntfs3g

# extracting vdbench files
RUN dnf -y install unzip && unzip /vdbench/vdbench50407.zip -d /vdbench/

# skip: starting the vdbench runner
# ENTRYPOINT /bin/bash -c "/vdbench/vdbench_runner.sh"

RUN chmod +x /vdbench/vdbench
# Remove -d64 flag - not supported in Java 10+
RUN sed -i 's/-d64//g' /vdbench/vdbench

# scale support - state signal
RUN dnf install -y python3 python3-pip

# install state-signals (--no-cache-dir for take always the latest)
RUN python3 -m pip --no-cache-dir install --upgrade pip && pip3 --no-cache-dir install state-signals==0.5.2

COPY state_signals_responder.py /state_signals_responder.py

#podman build -t quay.io/benchmark-runner/vdbench5.04.07:f43 . --no-cache
