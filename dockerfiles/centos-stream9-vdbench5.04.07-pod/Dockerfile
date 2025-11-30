FROM quay.io/centos/centos:stream9
# copying vdbench
COPY vdbench50407.zip  /vdbench/vdbench50407.zip
COPY vdbench_runner.sh /vdbench/vdbench_runner.sh

# Install Java 8 (OpenJDK 1.8) and set alternatives
RUN yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel \
    && alternatives --install /usr/bin/java java /usr/lib/jvm/java-1.8.0-openjdk/bin/java 1 \
    && alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-1.8.0-openjdk/bin/javac 1 \
    && alternatives --set java /usr/lib/jvm/java-1.8.0-openjdk/bin/java \
    && alternatives --set javac /usr/lib/jvm/java-1.8.0-openjdk/bin/javac

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
# install python 3.12 - take several minutes
RUN dnf install -y python3.12 python3.12-pip

# install state-signals (--no-cache-dir for take always the latest)
RUN python3.12 -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install state-signals==0.5.2

COPY state_signals_responder.py /state_signals_responder.py

#podman build -t quay.io/ebattat/centos-stream9-vdbench5.04.07-pod:latest . --no-cache
