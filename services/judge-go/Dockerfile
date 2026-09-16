# judge-go — bake-off nomzod A
#
# Ikki bosqich: (1) nsjail va worker quriladi, (2) ishga tushirish muhiti.
# Ishga tushirish muhitida submission tillari bo'ladi, LEKIN DB mijozi YO'Q.

# ── 1. nsjail ────────────────────────────────────────────────────────
FROM debian:trixie AS nsjail-build
RUN apt-get update && apt-get install -y --no-install-recommends \
        git ca-certificates build-essential pkg-config \
        bison flex protobuf-compiler libprotobuf-dev \
        libnl-3-dev libnl-route-3-dev \
    && rm -rf /var/lib/apt/lists/*
ARG NSJAIL_REF=master
# `NSJAIL_REF` — bu qadamning kesh kaliti. Natija Docker qatlam keshida
# saqlanadi: `NSJAIL_REF` va buyruq matni o'zgarmasa, klonlash va `make`
# UMUMAN ishlamaydi (keshdan olinadi).
#
# `--mount=type=cache` bu yerda ATAYLAB YO'Q: u `make` ning obyekt
# fayllarini saqlab qolardi, lekin `git clone` yangi ish katalogini
# yaratadi, ya'ni obyektlar baribir qayta qurilardi — foyda yo'q, faqat
# murakkablik qo'shilardi. Qatlam keshi shu ishni to'liq bajaradi.
#
# Diqqat: `master` — harakatlanuvchi havola. Yangi commit chiqsa ham
# Docker buni BILMAYDI va keshdan oladi. Sandbox versiyasini ataylab
# yangilash kerak bo'lganda `--build-arg NSJAIL_REF=<commit-sha>` bering.
RUN git clone --depth 1 --branch "${NSJAIL_REF}" https://github.com/google/nsjail.git /src \
    && cd /src && make -j"$(nproc)"

# ── 2. worker ────────────────────────────────────────────────────────
FROM golang:1.25-bookworm AS go-build
WORKDIR /app
COPY go.mod go.sum* ./
# `--mount=type=cache,target=/go/pkg/mod` — Go modul keshi qatlam keshidan
# ALOHIDA saqlanadi. `go.sum` o'zgarmasa modullar umuman yuklanmaydi;
# o'zgarganda faqat YANGI modul olinadi (api/web Dockerfile'lardagi
# pip/npm kesh bilan bir xil qoida).
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download
COPY *.go ./
# Kompilyatsiya keshi ham alohida: `golang:1.25-bookworm` image'ida
# GOCACHE allaqachon `/root/.cache/go-build`, ya'ni `go build` uni
# ishlatadi. Uni ham konteyner qatlami sifatida saqlash `go mod download`
# qatlamini har build'da takrorlanishdan qutqaradi.
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -o /out/judge-go .

# ── 3. runtime ───────────────────────────────────────────────────────
FROM debian:trixie-slim

# Manba commit yorlig'i — `tools/check_deploy.sh` shu orqali ishlab turgan
# binary manbadan eskimi yoki yo'qmi aniqlaydi.
#
# Nega kerak: Go binari uchun fayl hash'i solishtirib bo'lmaydi (web'dagi
# `.next` kabi), shuning uchun judge uzoq vaqt KO'R NUQTA edi — 2026-09-16
# da tuzatilgan wall-kill kodi commit qilinib CI'da tasdiqlangan, ishlab
# turgan konteyner esa eski binarda qolgan va buni hech narsa ko'rsatmagan.
#
# ⚠️ `unknown` — ataylab: qiymat compose'dan (`GIT_SHA`) keladi, ya'ni
# yorliqsiz build «noma'lum» deb O'QILADI va `check_deploy.sh` uni
# «tekshirilmadi» deb hisoblaydi, «mos» deb emas.
ARG GIT_SHA=unknown
LABEL org.rankwant.git-sha=$GIT_SHA
RUN apt-get update && apt-get install -y --no-install-recommends \
        # nsjail runtime bog'liqliklari (trixie t64 o'tishi: libprotobuf32t64)
        libprotobuf32t64 libnl-3-200 libnl-route-3-200 \
        # submission tillari (MVP: C++, Python, Java — 09-development-plan)
        # trixie: GCC 14 (to'liq C++23), Python 3.13, JDK 21
        g++ python3 openjdk-21-jdk-headless \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# JDK kutubxonalari loader KESHIGA qo'shiladi.
#
# `javac` va `java` — kichik launcher'lar; ular `libjli.so` ni RPATH dagi
# `$ORIGIN/../lib` orqali topadi, `$ORIGIN` esa dinamik loader tomonidan
# `/proc/self/exe` dan olinadi. Sandbox `/proc` ustiga bo'sh tmpfs qo'yadi
# (host jarayonlarini yashirish uchun), ya'ni `$ORIGIN` yechilmaydi va
# HAR BIR Java yuborishi «libjli.so: cannot open shared object file»
# bilan CE olardi — o'lchandi: uchta tildan biri butunlay ishlamasdi.
#
# Kesh orqali topilsa `$ORIGIN` kerak emas, `/proc` esa bo'sh qolaveradi.
# O'lchandi: bu katalogdagi 34 ta kutubxonaning birortasi ham tizim
# kutubxonasi nomini to'smaydi.
RUN echo /usr/lib/jvm/java-21-openjdk-amd64/lib > /etc/ld.so.conf.d/jdk.conf && ldconfig

COPY --from=nsjail-build /src/nsjail /usr/local/bin/nsjail
COPY --from=go-build     /out/judge-go /usr/local/bin/judge-go

# cgroup subtree'ni worker RUNTIME da yaratadi (/sys/fs/cgroup build vaqtida read-only).
# Konteyner --privileged yoki --cap-add=SYS_ADMIN --cgroupns=host bilan ishlashi kerak.

ENV REDIS_URL=redis://redis:6379/0
ENTRYPOINT ["/usr/local/bin/judge-go"]
