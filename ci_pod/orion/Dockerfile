FROM quay.io/fedora/python-314:latest AS builder

USER 0

RUN dnf install -y \
    git \
    gcc \
    make \
    rust \
    cargo \
    openssl-devel \
    python3-devel \
    pkg-config \
    && dnf clean all

WORKDIR /build

RUN git clone --depth 1 https://github.com/cloud-bulldozer/orion.git . && \
    pip install --upgrade pip && \
    pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir --no-binary cryptography cryptography && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir .

RUN ORION_PATH=$(which orion) && \
    ORION_DIR=$(dirname "$ORION_PATH") && \
    mkdir -p "/install${ORION_DIR}" && \
    cp "$ORION_PATH" "/install${ORION_PATH}" && \
    for sp in $(python3 -c "import site; print(' '.join(site.getsitepackages()))"); do \
        if [ -d "$sp" ]; then \
            mkdir -p "/install${sp}" && \
            cp -r "$sp"/* "/install${sp}/"; \
        fi; \
    done

FROM quay.io/fedora/python-314:latest

ENV PYTHONUNBUFFERED="1"

USER 0
RUN dnf install -y openssl && dnf clean all

COPY --from=builder /install/ /

USER 1001

ENTRYPOINT ["orion"]
