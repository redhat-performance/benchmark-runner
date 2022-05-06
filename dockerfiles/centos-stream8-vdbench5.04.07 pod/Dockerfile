FROM quay.io/centos/centos:stream8
# copying vdbench
COPY vdbench50407.zip  /vdbench/vdbench50407.zip
COPY vdbench_runner.sh /vdbench/vdbench_runner.sh

# installing java
RUN yum -y install java

# installing vim
RUN yum -y install vim

# installing monitoring tools
RUN yum -y install procps
RUN yum -y install sysstat

# add ntfs & xfs support
ENV NTFS=ntfs3g
COPY ${NTFS}  /${NTFS}
WORKDIR ${NTFS}
RUN yum -y install xfsprogs
RUN yum -y groupinstall "Development Tools" \
    && tar -xvf ntfs-3g_ntfsprogs-2017.3.23.tgz --strip-components 1 \
    && ./configure --prefix=/usr/local --disable-static \
    && make \
    && make install

#delete installation files
WORKDIR /root
RUN rm -rf /ntfs3g

# extracting vdbench files
RUN /bin/bash -c "unzip /vdbench/vdbench50407.zip -d /vdbench/"

# skip: starting the vdbench runner
# ENTRYPOINT /bin/bash -c "/vdbench/vdbench_runner.sh"

RUN chmod +x /vdbench/vdbench

# scale support - state signal
# install python 3.9 - take several minutes
RUN dnf install -y python3.9

# install state-signals (--no-cache-dir for take always the latest)
RUN python3.9 -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install state-signals==0.5.2

COPY state_signals_responder.py /state_signals_responder.py

#podman build -t quay.io/ebattat/centos-stream8-vdbench5.04.07-pod:latest . --no-cache
