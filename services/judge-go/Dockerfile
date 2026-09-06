# judge-go — bake-off nomzod A
#
# Ikki bosqich: (1) nsjail va worker quriladi, (2) ishga tushirish muhiti.
# Ishga tushirish muhitida submission tillari bo'ladi, LEKIN DB mijozi YO'Q.

# ── 1. nsjail ────────────────────────────────────────────────────────
FROM debian:bookworm AS nsjail-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates build-essential pkg-config \
        bison flex protobuf-compiler libprotobuf-dev \
        libnl-3-dev libnl-route-3-dev \
    && rm -rf /var/lib/apt/lists/*
ARG NSJAIL_REF=master
RUN git clone --depth 1 --branch "${NSJAIL_REF}" https://github.com/google/nsjail.git /src \
    && cd /src && make -j"$(nproc)"

# ── 2. worker ────────────────────────────────────────────────────────
FROM golang:1.22-bookworm AS go-build
WORKDIR /app
COPY go.mod go.sum* ./
RUN go mod download
COPY *.go ./
RUN CGO_ENABLED=0 go build -trimpath -o /out/judge-go .

# ── 3. runtime ───────────────────────────────────────────────────────
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
        # nsjail runtime bog'liqliklari
        libprotobuf32 libnl-3-200 libnl-route-3-200 \
        # submission tillari (MVP: C++, Python, Java — 09-development-plan)
        g++ python3 openjdk-17-jdk-headless \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=nsjail-build /src/nsjail /usr/local/bin/nsjail
COPY --from=go-build     /out/judge-go /usr/local/bin/judge-go

# cgroup subtree'ni worker RUNTIME da yaratadi (/sys/fs/cgroup build vaqtida read-only).
# Konteyner --privileged yoki --cap-add=SYS_ADMIN --cgroupns=host bilan ishlashi kerak.

ENV REDIS_URL=redis://redis:6379/0
ENTRYPOINT ["/usr/local/bin/judge-go"]
