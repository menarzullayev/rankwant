# judge-py — bake-off nomzod B
#
# DIQQAT: isolate cgroup v1 ga tayanadi. Zamonaviy host cgroup v2 da bo'lsa,
# GRUB ga `systemd.unified_cgroup_hierarchy=0 systemd.legacy_systemd_cgroup_controller=1`
# yozib qayta yuklash kerak. Bu bake-off'ning asosiy o'lchov nuqtalaridan biri.

FROM debian:bookworm AS isolate-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates build-essential pkg-config \
        libcap-dev libsystemd-dev libseccomp-dev asciidoc-base \
    && rm -rf /var/lib/apt/lists/*
ARG ISOLATE_REF=master
# `make install` binary'ni ham, default.cf konfiguratsiyasini ham joylaydi
# (repoda faqat default.cf.in shabloni bor).
RUN git clone --depth 1 --branch "${ISOLATE_REF}" https://github.com/ioi/isolate.git /src \
    && cd /src \
    && make isolate isolate-cg-keeper \
    && make install PREFIX=/opt/isolate SBINDIR=/opt/isolate/bin \
         SYSCONFDIR=/opt/isolate/etc VARDIR=/var/local/lib/isolate \
         MANDIR=/opt/isolate/man 2>/dev/null || true \
    && mkdir -p /opt/isolate/bin /opt/isolate/etc \
    && cp /src/isolate /opt/isolate/bin/ \
    && sed -e 's|@BOXDIR@|/var/local/lib/isolate|; s|@BOXUID@|65534|; s|@BOXGID@|65534|; \
               s|@CONFIGDIR@|/opt/isolate/etc|; s|@VERSION@|bakeoff|' \
           /src/default.cf.in > /opt/isolate/etc/isolate.conf \
    && cp /src/isolate-check-environment /opt/isolate/bin/ 2>/dev/null || true

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcap2 libsystemd0 libseccomp2 \
        g++ python3 python3-pip openjdk-17-jdk-headless \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=isolate-build /opt/isolate/bin/ /usr/local/bin/
COPY --from=isolate-build /opt/isolate/etc/ /usr/local/etc/
# isolate master user namespace ishlatadi: `isolate` foydalanuvchisi va unga
# subuid/subgid diapazoni kerak, aks holda --init "User isolate not found in
# /etc/subuid" bilan yiqiladi.
RUN useradd -r -u 61000 -s /usr/sbin/nologin isolate \
    && echo "isolate:100000:65536" >> /etc/subuid \
    && echo "isolate:100000:65536" >> /etc/subgid \
    && chmod u+s /usr/local/bin/isolate \
    && mkdir -p /var/local/lib/isolate

WORKDIR /app
RUN pip install --no-cache-dir --break-system-packages "redis>=5.0"
COPY *.py ./

ENV REDIS_URL=redis://redis:6379/0
ENTRYPOINT ["python3", "main.py"]
