# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

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
COPY . .

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
LABEL org.rankwant.git-sha=$GIT_SHA
LABEL org.rankwant.built-at=$BUILT_AT

RUN python manage.py collectstatic --noinput || true

# DIQQAT: bu konteynerda foydalanuvchi kodi ISHLAMAYDI.
# Judge alohida hostda — 06-architecture 🔒 xavfsizlik chegarasi.
EXPOSE 8000
ENV GUNICORN_WORKERS=4
# Shell — `GUNICORN_WORKERS` compose'dan keladi (50k: api replica × worker).
CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS}
