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

#: One piece is at most `speech.SEGMENT_CHARS` characters: measured ~10 s on the GPU. The
#: first piece after an idle spell also waits for the host supervisor to load the voice
#: (`services/tts/supervisor.py`, up to its `TTS_LOAD_TIMEOUT_S` = 150 s): measured 73 s in
#: production on 2026-11-12, so the first piece took 82 s against the old 120 s limit. A
#: worker that gave up first would leave the piece unmade for the claim's 10 minutes.
SYNTHESIS_TIMEOUT_S = 210


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
