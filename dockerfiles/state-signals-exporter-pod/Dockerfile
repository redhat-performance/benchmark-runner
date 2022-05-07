FROM quay.io/centos/centos:stream8

# Update and use not only best candidate packages (avoiding failures)
RUN dnf update -y --nobest

# install python 3.9 - take several minutes
RUN dnf install -y python3.9

# install state-signals (--no-cache-dir for take always the latest)
RUN python3 -m pip --no-cache-dir install --upgrade pip && pip --no-cache-dir install state-signals==0.5.2

COPY state_signals_exporter.py /state_signals_exporter.py
