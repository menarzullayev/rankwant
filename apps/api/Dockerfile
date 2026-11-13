# syntax=docker/dockerfile:1
FROM python:3.14-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Never root at run time (Docker Scout: "runs as the root user"). uid 10001, the
# same number the hiso_box and cpstands images use. It owns /app, so `collectstatic`
# below and the `celerybeat-schedule` file that `celery beat` keeps in its working
# directory both work; nothing else is written at run time (PYTHONDONTWRITEBYTECODE).
RUN useradd --system --uid 10001 --create-home --home-dir /home/app --shell /usr/sbin/nologin app \
    && chown app:app /app

COPY requirements.lock ./
# --mount=type=cache: pip paketlari host'da /root/.cache/pip da saqlanadi.
# requirements.lock o'zgarganda ham faqat YANGI paketlar yuklanadi,
# avval yuklanganlar keshdan olinadi (~10x tezroq).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.lock

# Butun kod ENG OXIRIDA: bu qatlam har commit'da o'zgaradi, ya'ni
# undan keyin og'ir qatlam turmasligi kerak.
#
# `collectstatic` shu sababli `COPY . .` dan KEYIN qoladi (u statik
# fayl manbalarini o'qiydi, ya'ni kod kontekstda bo'lishi shart).
# Uning narxi ARZON: o'lchandi — ~0.4 s, shuning uchun `COPY . .`
# qatlami bilan birga yangilanishi build'ni sezilarli cho'zmaydi.
# Uni alohida qatlam qilib `COPY config/ ./config/` bilan oldinga
# chiqarish ham mumkin edi, lekin `core/` va boshqa ilovalarga ham
# bog'liq — qo'shimcha mo'rtlikka arzimaydi.
COPY --chown=app:app . .

# Build tamg'asi — "image eskimi?" savoliga javob beradigan yagona ishonchli
# belgi. `tools/check_deploy.sh` aynan shu label'ni o'qiydi.
#
# NEGA KERAK: CI (`ci-local.sh api`) MANBA kodni vaqtinchalik konteynerga
# o'rnatib sinaydi, ishlab turgan `rankwant-api` image'i esa umuman
# tekshirilmaydi. Natijada CI yashil bo'lib tursa ham produksiya ESKI
# kodni ko'rsatishi mumkin — 2026-09-13 dagi uch avariya aynan shundan.
#
# `apps/api/.dockerignore` dan `.git` chiqarib tashlanmagan bo'lsa ham
# commit'ni tashqaridan uzatish to'g'riroq: `.dockerignore` o'zgarsa
# label jimgina `unknown` bo'lib qolardi.
ARG GIT_SHA=unknown
ARG BUILT_AT=unknown
# `ENV` too: a `LABEL` is invisible from inside the running container, and
# `/api/v1/version/` has to report the commit this process was built from.
ENV GIT_SHA=$GIT_SHA
LABEL org.rankwant.git-sha=$GIT_SHA
LABEL org.rankwant.built-at=$BUILT_AT

# Settings refuse to load without a secret key (ADR-0044). `collectstatic`
# signs nothing, so a build-only value is enough — and without it the
# `|| true` below would swallow the failure and ship an image with no
# static files.
USER app
RUN DJANGO_SECRET_KEY=build-only-not-a-secret python manage.py collectstatic --noinput || true

# DIQQAT: bu konteynerda foydalanuvchi kodi ISHLAMAYDI.
# Judge alohida hostda — 06-architecture 🔒 xavfsizlik chegarasi.
EXPOSE 8000
ENV GUNICORN_WORKERS=4
# Shell — `GUNICORN_WORKERS` compose'dan keladi (50k: api replica × worker).
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS}

# Course video encoding (ADR-0056 § 3.5): only the `video-worker` service
# builds this stage (`target: video`). ffmpeg is not in the API image.
FROM base AS video
USER root
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*
USER app
CMD ["celery", "-A", "config", "worker", "-Q", "video", "--concurrency", "1", "-l", "info"]

# AI tutor (ADR-0065 § 2.6): only the `ai-worker` service builds this stage
# (`target: ai`). The npm package installs one native `claude` binary, so Node
# is needed to fetch it and not to run it: the binary alone is copied over
# (measured: 1.0 GB instead of 1.9 GB with Node and npm in the image). The
# version is pinned — an update changes how `claude -p` behaves.
FROM node:26-bookworm-slim AS claude-cli
RUN npm install -g @anthropic-ai/claude-code@2.1.318     && cp "$(npm root -g)/@anthropic-ai/claude-code/bin/claude.exe" /claude

FROM base AS ai
COPY --from=claude-cli /claude /usr/local/bin/claude
ENV DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
CMD ["celery", "-A", "config", "worker", "-Q", "ai", "--concurrency", "2", "-l", "info"]

# The default target stays the plain API image: a stage that changes
# nothing, last in the file.
FROM base AS app
