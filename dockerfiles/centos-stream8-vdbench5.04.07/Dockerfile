FROM quay.io/centos/centos:stream8
# copying vdbench
COPY /vdbench_linux  /vdbench
COPY vdbench_runner.sh /vdbench/vdbench_runner.sh

# installing java
RUN yum -y install java

# installing vim
RUN yum -y install vim

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

# Run vdbench runner
RUN /bin/bash -c "/vdbench/vdbench_runner.sh"
