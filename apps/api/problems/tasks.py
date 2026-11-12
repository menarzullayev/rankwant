"""Background work of the `problems` app."""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request

from celery import shared_task
from django.conf import settings

from problems import speech_audio

log = logging.getLogger(__name__)

#: One piece is at most `speech.SEGMENT_CHARS` characters: measured ~10 s on the GPU.
SYNTHESIS_TIMEOUT_S = 120


@shared_task(name="problems.synthesize_speech")
def synthesize_speech(key: str, text: str) -> str:
    """Make one audio piece on the voice service and keep it (ADR-0064 § 5).

    Runs on the `tts` queue, in `tts-worker`, one at a time — the GPU holds
    one model. A piece already in storage is not made again.
    """
    if speech_audio.exists(key):
        return "exists"
    request = urllib.request.Request(
        settings.TTS_URL.rstrip("/") + "/synthesize",
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=SYNTHESIS_TIMEOUT_S) as response:
            audio = response.read()
            model = response.headers.get("X-Model", "")
    except (urllib.error.URLError, TimeoutError) as exc:
        log.warning("speech piece %s failed: %s", key, exc)
        return "failed"
    if model and model != settings.TTS_MODEL:
        # The service reads with another voice than the key was named for:
        # keeping the file would serve the wrong voice under this name.
        log.warning("speech piece %s: service model %s ≠ %s", key, model, settings.TTS_MODEL)
        return "model_mismatch"
    speech_audio.put(key, audio)
    return "made"
