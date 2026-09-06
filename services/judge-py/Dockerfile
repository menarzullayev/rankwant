# judge-py — bake-off nomzod B
#
# DIQQAT: isolate cgroup v1 ga tayanadi. Zamonaviy host cgroup v2 da bo'lsa,
# GRUB ga `systemd.unified_cgroup_hierarchy=0 systemd.legacy_systemd_cgroup_controller=1`
# yozib qayta yuklash kerak. Bu bake-off'ning asosiy o'lchov nuqtalaridan biri.

FROM debian:bookworm AS isolate-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates build-essential pkg-config \
        libcap-dev libsystemd-dev asciidoc-base \
    && rm -rf /var/lib/apt/lists/*
ARG ISOLATE_REF=master
RUN git clone --depth 1 --branch "${ISOLATE_REF}" https://github.com/ioi/isolate.git /src \
    && cd /src && make isolate

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcap2 libsystemd0 \
        g++ python3 python3-pip openjdk-17-jdk-headless \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=isolate-build /src/isolate /usr/local/bin/isolate
COPY --from=isolate-build /src/default.cf /usr/local/etc/isolate
RUN chmod u+s /usr/local/bin/isolate

WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir --break-system-packages "redis>=5.0"
COPY *.py ./

ENV REDIS_URL=redis://redis:6379/0
ENTRYPOINT ["python3", "main.py"]
