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
#
# The module cache is mounted here as well. `go mod download` fills the cache
# mount, not the layer, so without it `go build` fetched all 21 modules again on
# every Go change (measured), and a dropped connection to proxy.golang.org
# failed the build on the CI engine.
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -o /out/judge-go .

# ── 3. toolchain archives ────────────────────────────────────────────
# Languages Debian trixie does not ship, or ships too old (ADR-0022). Every
# archive is checked against the checksum its vendor publishes; curl and unzip
# stay in this stage and never reach the image that runs submissions.
FROM debian:trixie-slim AS toolchains
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl unzip xz-utils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /dl

# .NET SDK 10.0.401 — C# 14. Checksum: release-metadata/10.0/releases.json (sha512).
RUN curl -fsSL --retry 3 -o dotnet.tgz https://builds.dotnet.microsoft.com/dotnet/Sdk/10.0.401/dotnet-sdk-10.0.401-linux-x64.tar.gz \
    && echo "51c8b999af9e8dd9998c9edc5944e19a90788862068acd38694e098889054ce8c23d4f0c5cccfa16bf187d044562359e5ee69a9f8ad0bbe913ba90311fbce25b  dotnet.tgz" | sha512sum -c - \
    && mkdir -p /opt/dotnet && tar -xzf dotnet.tgz -C /opt/dotnet && rm dotnet.tgz

# Node.js 24.21.0 LTS — JavaScript. Debian's Node 20 reached end of life in April 2026.
RUN curl -fsSL --retry 3 -o node.txz https://nodejs.org/dist/v24.21.0/node-v24.21.0-linux-x64.tar.xz \
    && echo "fd8e59d5a511510f6a298afb548f18c7d2b1be404d8b4a27d94fbe49f56cb2d6  node.txz" | sha256sum -c - \
    && mkdir -p /opt/node && tar -xJf node.txz -C /opt/node --strip-components=1 && rm node.txz

# Kotlin 2.4.20 — Debian has 1.3.31 (2019).
RUN curl -fsSL --retry 3 -o kotlin.zip https://github.com/JetBrains/kotlin/releases/download/v2.4.20/kotlin-compiler-2.4.20.zip \
    && echo "59e9ca74c7904ef2c122b12114937673ccce68de820a663f0ed66ccf8799e0b7  kotlin.zip" | sha256sum -c - \
    && unzip -q kotlin.zip -d /opt && rm kotlin.zip

# Dart 3.13.4 — not in Debian. Checksum: the .sha256sum file published next to the zip.
RUN curl -fsSL --retry 3 -o dart.zip https://storage.googleapis.com/dart-archive/channels/stable/release/3.13.4/sdk/dartsdk-linux-x64-release.zip \
    && echo "6487a10df5eab890d746d14a55f4c70bec3c1c0633f51804eb504cbc0fc395bb  dart.zip" | sha256sum -c - \
    && unzip -q dart.zip -d /opt && rm dart.zip

# Scala 3.9.0 — Debian has 2.11. Checksum: the release's .sha256 asset. The bundled
# scala-cli (146 MB) only serves the `scala` runner; scalac never calls it.
RUN curl -fsSL --retry 3 -o scala.tgz https://github.com/scala/scala3/releases/download/3.9.0/scala3-3.9.0-x86_64-pc-linux.tar.gz \
    && echo "0815d7aa2838fc5c806d3f228ad6e1f6a4421f57fa5407dad3698b91b94b3ec0  scala.tgz" | sha256sum -c - \
    && mkdir -p /opt/scala && tar -xzf scala.tgz -C /opt/scala --strip-components=1 && rm scala.tgz \
    && rm /opt/scala/libexec/scala-cli

# ── 4. runtime ───────────────────────────────────────────────────────
FROM debian:trixie-slim

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

# Group 1 (ADR-0022): Rust 1.85, Go 1.24, PHP 8.4. C uses the GCC 14 above.
# libicu76 is for .NET: without ICU the runtime aborts before Main runs.
RUN apt-get update && apt-get install -y --no-install-recommends \
        rustc golang-go php-cli libicu76 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=toolchains /opt/dotnet /opt/dotnet
COPY --from=toolchains /opt/node /opt/node
COPY --from=toolchains /opt/kotlinc /opt/kotlinc

# Go: export data for the whole standard library. A submission compiles with
# `go tool compile` and `go tool link` against it, so nothing in the sandbox
# needs a writable build cache — and it costs ~90 ms of CPU instead of ~5.6 s
# for `go build` on an empty cache (measured).
RUN export GOROOT=/usr/lib/go-1.24 GOTELEMETRY=off CGO_ENABLED=0 GOCACHE=/opt/go-std/cache \
    && go build std \
    && go list -export -f '{{if .Export}}packagefile {{.ImportPath}}={{.Export}}{{end}}' std > /opt/go-std/importcfg \
    && chmod -R a+rX /opt/go-std

# .NET: `dotnet exec` reads one shared runtimeconfig, and csc takes the
# reference assemblies from a response file — no project, no restore, no network.
RUN mkdir -p /opt/rankwant/dotnet && cd /opt/rankwant/dotnet \
    && ref="$(ls -d /opt/dotnet/packs/Microsoft.NETCore.App.Ref/*/ref/net10.0)" \
    && runtime="$(ls /opt/dotnet/shared/Microsoft.NETCore.App)" \
    && printf '{"runtimeOptions":{"tfm":"net10.0","framework":{"name":"Microsoft.NETCore.App","version":"%s"}}}\n' "$runtime" > app.runtimeconfig.json \
    && { echo "-nologo"; echo "-optimize+"; ls "$ref"/*.dll | sed 's/^/-r:/'; } > csc.rsp \
    && ln -s "$(ls -d /opt/dotnet/sdk/*/Roslyn/bincore)" roslyn

# Group 2 (ADR-0022): Pascal, Ruby, Haskell, R, Swift, Perl, D, OCaml. TypeScript runs on
# the Node.js above; Dart and Scala come from the archive stage. Every group sits below
# the previous one, so adding a group leaves the earlier layers cached.
RUN apt-get update && apt-get install -y --no-install-recommends \
        fp-compiler fp-units-rtl ruby ghc r-base-core swiftlang perl ldc ocaml-nox ocaml-findlib \
    && rm -rf /var/lib/apt/lists/*

COPY --from=toolchains /opt/dart-sdk /opt/dart-sdk
COPY --from=toolchains /opt/scala /opt/scala

# GHC's libraries go into the loader cache, like the JDK's: ghc looks for them through
# $ORIGIN, which cannot resolve under the /proc mask. The directory holds only libHS*
# libraries (measured: 39), so no system library is shadowed.
RUN ls -d /usr/lib/ghc/lib/x86_64-linux-ghc-* > /etc/ld.so.conf.d/ghc.conf && ldconfig

# The toolchain layers above stay cached across deploys: an ARG in scope makes
# every later RUN miss the cache when its value changes, and GIT_SHA changes
# on every commit.
#
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

COPY --from=nsjail-build /src/nsjail /usr/local/bin/nsjail
COPY --from=go-build     /out/judge-go /usr/local/bin/judge-go

# cgroup subtree'ni worker RUNTIME da yaratadi (/sys/fs/cgroup build vaqtida read-only).
# Konteyner --privileged yoki --cap-add=SYS_ADMIN --cgroupns=host bilan ishlashi kerak.

ENV REDIS_URL=redis://redis:6379/0
ENTRYPOINT ["/usr/local/bin/judge-go"]
