# Mahalliy CI uchun dev muhit — `rankwant-api` ustiga test bog'liqliklari.
#
# Nega alohida image: `pip install -r requirements-dev.lock` har ishga
# tushirishda ~30 soniya yeydi, chunki `docker run --rm` har safar toza
# konteyner beradi. Bir marta qurib, keyin qayta ishlatilsa o'sha 30
# soniya butunlay yo'qoladi.
#
# Teg LOCK FAYL XESHIGA bog'lanadi (`tools/ci-local.sh`), ya'ni
# `requirements-dev.lock` o'zgarsa image o'zi qayta quriladi — eskirib
# qolmaydi.

ARG BASE=rankwant-api:latest
FROM ${BASE}

COPY apps/api/requirements-dev.lock /tmp/requirements-dev.lock
RUN pip install --no-cache-dir -r /tmp/requirements-dev.lock \
    && rm /tmp/requirements-dev.lock
