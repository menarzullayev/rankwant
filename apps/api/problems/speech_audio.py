"""The voice's audio pieces: made on demand, kept in object storage (ADR-0064 § 5).

A piece is named by `speech.cache_key(model, text)`, so the same model reading
the same text is made once for everyone, and an edited sentence or another
model gets a new name — nothing stale is ever served. The files never change,
so the API serves them with an immutable cache header and the edge keeps them.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from django.conf import settings
from django.core.cache import cache

from core.cache import cache_get, cache_set

log = logging.getLogger(__name__)

PREFIX = "speech/"
#: MP3: Ogg/Opus is smaller, but older Safari does not play it.
CONTENT_TYPE = "audio/mpeg"
EXT = ".mp3"
#: A key is the first 40 hex characters of a SHA-256 (`speech.cache_key`).
KEY = re.compile(r"^[0-9a-f]{40}$")
#: A piece asked for in the last 10 minutes is not queued again.
PENDING_SECONDS = 600


def enabled() -> bool:
    """The voice service is configured (`TTS_URL`); otherwise there is no audio."""
    return bool(settings.TTS_URL)


def _client() -> Any:
    from problems.storage import client

    return client()


def claim(key: str) -> bool:
    """Mark a piece as asked for; `False` when it already is (do not queue it twice)."""
    try:
        return bool(cache.add(pending_key(key), True, PENDING_SECONDS))
    except Exception:
        return True  # a cache outage must not stop the voice; the worker dedupes on storage


def _ready_key(key: str) -> str:
    return f"speech:ready:{key}"


def pending_key(key: str) -> str:
    return f"speech:pending:{key}"


def exists(key: str) -> bool:
    """The piece is in storage. A found piece is remembered: it never goes away."""
    if cache_get(_ready_key(key)):
        return True
    try:
        _client().head_object(Bucket=settings.S3_BUCKET, Key=PREFIX + key + EXT)
    except Exception:
        return False
    cache_set(_ready_key(key), True, 86_400)
    return True


def put(key: str, data: bytes) -> None:
    _client().put_object(
        Bucket=settings.S3_BUCKET, Key=PREFIX + key + EXT, Body=data, ContentType=CONTENT_TYPE
    )
    cache_set(_ready_key(key), True, 86_400)


def get(key: str) -> bytes | None:
    if not KEY.match(key):
        return None
    try:
        body = _client().get_object(Bucket=settings.S3_BUCKET, Key=PREFIX + key + EXT)["Body"]
        data: bytes = body.read()
    except Exception:
        return None
    return data
