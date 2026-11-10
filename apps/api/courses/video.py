"""Video references of course lessons (ADR-0056 § 3.5).

An author may paste a whole link; the lesson keeps only the provider's id,
because the page builds the embed address from it and the id ends up in a
frame's `src`. Anything that is not a plain id after normalising is refused.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
VIMEO_ID = re.compile(r"^\d{1,12}$")
#: An R2 key prefix of an HLS rendition: lower-case path segments.
HLS_KEY = re.compile(r"^[a-z0-9][a-z0-9/_-]{0,190}$")

_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}
_VIMEO_HOSTS = {"vimeo.com", "www.vimeo.com", "player.vimeo.com"}


def _youtube(ref: str) -> str:
    url = urlparse(ref if "//" in ref else f"//{ref}") if ("/" in ref or "." in ref) else None
    if url is None:
        return ref
    host = (url.hostname or "").lower()
    if host == "youtu.be":
        return url.path.strip("/").split("/")[0]
    if host in _YOUTUBE_HOSTS:
        if url.path == "/watch":
            return (parse_qs(url.query).get("v") or [""])[0]
        parts = [p for p in url.path.split("/") if p]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live", "v"}:
            return parts[1]
    return ref


def _vimeo(ref: str) -> str:
    if "/" not in ref and "." not in ref:
        return ref
    url = urlparse(ref if "//" in ref else f"//{ref}")
    if (url.hostname or "").lower() not in _VIMEO_HOSTS:
        return ref
    parts = [p for p in url.path.split("/") if p]
    numeric = [p for p in parts if p.isdigit()]
    return numeric[0] if numeric else ref


def normalise(provider: str, ref: str) -> str:
    """The id to store for `ref` under `provider`; `ValueError` if none."""
    ref = ref.strip()
    if not ref:
        return ""
    if provider == "youtube":
        value = _youtube(ref)
        if YOUTUBE_ID.match(value):
            return value
        raise ValueError("Give a YouTube video link or its 11-character id.")
    if provider == "vimeo":
        value = _vimeo(ref)
        if VIMEO_ID.match(value):
            return value
        raise ValueError("Give a Vimeo video link or its numeric id.")
    if provider == "hls":
        if HLS_KEY.match(ref) and ".." not in ref:
            return ref
        raise ValueError("An R2 video key is a lower-case path.")
    raise ValueError("Choose where the video is hosted.")
