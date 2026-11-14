# The official PostgreSQL 16 image with two changes:
#
#   1. pending Debian updates are applied;
#   2. `gosu` is removed and the server starts as `postgres` directly.
#
# The official entrypoint uses `gosu` only to drop from root to `postgres`.
# It is a Go binary built with an old toolchain: on 2026-11-15 Docker Scout
# counted 4 critical and 30 high standard-library vulnerabilities in it, all
# of the critical ones in the image. Started as `postgres` the entrypoint
# never calls it (it tests `id -u` first), so nothing replaces it.
#
# The final stage is a flat copy on purpose: the scanner reads every layer,
# so a file deleted in a later layer still counts (measured on 2026-11-14).
# A flat copy drops the base image's configuration, which is why ENV,
# VOLUME, EXPOSE, STOPSIGNAL, ENTRYPOINT and CMD are restated below — the
# values are the official image's own (`docker image inspect postgres:16`).
#
# Running as `postgres` means the entrypoint cannot chown a data directory
# it does not own. A named volume is fine: an empty one takes the owner of
# the image's directory, and an existing one was written by the same uid
# (999). A bind mount owned by someone else would not start.
FROM postgres:16 AS official

RUN apt-get update \
 && apt-get upgrade -y \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /usr/local/bin/gosu

FROM scratch
COPY --from=official / /
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/postgresql/16/bin \
    LANG=en_US.utf8 \
    PG_MAJOR=16 \
    PGDATA=/var/lib/postgresql/data
VOLUME /var/lib/postgresql/data
EXPOSE 5432
STOPSIGNAL SIGINT
USER postgres
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
