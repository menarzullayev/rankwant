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

# The api image runs as `app` (uid 10001) since 2026-11-13. This image does
# not: it is the local test environment, never deployed. Its `pip install`
# writes to the system site-packages, and the test runs write into the
# bind-mounted checkout (`.pytest_cache`, `.mypy_cache`, coverage, the SQLite
# test database), whose owner is the host user, not uid 10001. As `app` the
# install below fell back to a per-user install and the build failed — the
# Nightly `readiness` job was red on 2026-11-14 for this reason alone.
USER root

COPY apps/api/requirements-dev.lock /tmp/requirements-dev.lock
RUN pip install --no-cache-dir -r /tmp/requirements-dev.lock \
    && rm /tmp/requirements-dev.lock
