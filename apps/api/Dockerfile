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
RUN python manage.py collectstatic --noinput || true

# DIQQAT: bu konteynerda foydalanuvchi kodi ISHLAMAYDI.
# Judge alohida hostda — 06-architecture 🔒 xavfsizlik chegarasi.
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
