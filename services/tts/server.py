"""The voice of problem statements (ADR-0064, phase 2): Navoiy on the host GPU.

Runs on the host with the Navoiy venv (`video-lab/tts/navoiy/.venv`: Python
3.10, torch 2.3.1+cu121), not in a container: that venv is the one the
2026-11-12 measurement ran in (RTF 0.84 on the RTX 2080 Ti), and a CUDA
image with the CosyVoice stack would add several GB to Docker's disk
(the 2026-11-11 disk rule). It listens on 127.0.0.1 only; containers reach
it as `host.docker.internal` (Docker Desktop forwards that to the host's
loopback — measured), the network does not.

    POST /synthesize  {"text": "..."}  → audio/mpeg (MP3, mono)
    GET  /health                       → {"model": "...", "ready": true}

One generation at a time: the GPU holds one model, and a second request
waits for the lock instead of running out of memory.

Environment:
    NAVOIY_ROOT        the `navoiy` folder (CosyVoice, CosyVoice2-0.5B, navoiy-tts)
    TTS_REFERENCE_WAV  the voice to clone — owner choice 2026-11-12: the FLEURS
                       recording (CC-BY 4.0), «keyinchalik vaziyatga qaraymiz»
    TTS_EMOTION        Navoiy's instruction set entry (default «xotirjam»)
    TTS_VOICE          the voice's short name, in the model name (default «fleurs»)
    TTS_PORT           default 8370
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("NAVOIY_ROOT", "D:/Linux/Web_Projects/video-lab/tts/navoiy"))
REFERENCE = Path(os.environ.get("TTS_REFERENCE_WAV", ""))
EMOTION = os.environ.get("TTS_EMOTION", "xotirjam")
#: The cloned voice's short name. It is part of the model name the API names
#: audio files with (`TTS_MODEL`), so another voice gets new files.
VOICE = os.environ.get("TTS_VOICE", "fleurs")
PORT = int(os.environ.get("TTS_PORT", "8370"))
MODEL_NAME = f"navoiy-{EMOTION}-{VOICE}"
#: A request longer than this is refused: the API sends one segment at a time.
MAX_CHARS = 1200
SAMPLE_RATE = 24000

_lock = threading.Lock()
_model: dict[str, Any] = {}


def plain_apostrophes(text: str) -> str:
    """The model saw the ASCII apostrophe in training (`bench_common.py`)."""
    return text.replace("ʻ", "'").replace("ʼ", "'").replace("‘", "'").replace("’", "'")


def load() -> None:
    cosy = ROOT / "CosyVoice"
    sys.path[:0] = [
        str(cosy),
        str(cosy / "third_party" / "Matcha-TTS"),
        str(ROOT / "navoiy-tts"),
    ]
    import torch
    from cosyvoice.cli.cosyvoice import CosyVoice2
    from uztts.normalize import normalize

    emotions = {
        e["uz"]: e
        for e in json.loads(
            (ROOT / "navoiy-tts" / "emotions_40h.json").read_text(encoding="utf-8")
        )
    }
    model = CosyVoice2(
        str(ROOT / "CosyVoice2-0.5B"), load_jit=False, load_trt=False, fp16=True
    )
    state = torch.load(
        ROOT / "navoiy-tts" / "emotion_600h_joint.pt",
        map_location="cpu",
        weights_only=True,
    )
    for key in ("state_dict", "model", "llm"):
        if isinstance(state.get(key), dict):
            state = state[key]
    model.model.llm.load_state_dict(state, strict=False)
    del state
    model.model.llm.eval()
    _model.update(
        torch=torch,
        model=model,
        normalize=normalize,
        instruction=emotions[EMOTION]["instruct"].strip() + "<|endofprompt|>",
    )


def synthesize(text: str) -> tuple[bytes, float]:
    """Text → MP3 (48 kbit/s, mono — every browser plays it), and its length in seconds."""
    torch = _model["torch"]
    spoken = _model["normalize"](plain_apostrophes(text), mode="infer")
    with _lock:
        torch.manual_seed(1)
        with torch.inference_mode():
            chunks = [
                p["tts_speech"].cpu()
                for p in _model["model"].inference_instruct2(
                    spoken,
                    _model["instruction"],
                    str(REFERENCE),
                    stream=False,
                    speed=1.0,
                )
            ]
    audio = torch.cat(chunks, dim=1).clamp(-1, 1)
    pcm = (audio * 32767).to(torch.int16).numpy().tobytes()
    encoded = subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-f",
            "s16le",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-i",
            "pipe:0",
            "-c:a",
            "libmp3lame",
            "-b:a",
            "48k",
            "-f",
            "mp3",
            "pipe:1",
        ],
        input=pcm,
        capture_output=True,
        check=True,
    ).stdout
    return encoded, audio.shape[-1] / SAMPLE_RATE


class Handler(BaseHTTPRequestHandler):
    server_version = "rankwant-tts/1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"model": MODEL_NAME, "ready": bool(_model)})
        else:
            self._json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/synthesize":
            self._json(404, {"error": "not_found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
            text = str(
                json.loads(self.rfile.read(length) or b"{}").get("text") or ""
            ).strip()
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "bad_request"})
            return
        if not text or len(text) > MAX_CHARS:
            self._json(400, {"error": "bad_text"})
            return
        started = time.monotonic()
        try:
            audio, seconds = synthesize(text)
        except Exception as exc:  # the API turns this into «try later»
            self._json(500, {"error": "synthesis_failed", "detail": type(exc).__name__})
            return
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(audio)))
        self.send_header("X-Audio-Seconds", f"{seconds:.2f}")
        self.send_header("X-Synthesis-Seconds", f"{time.monotonic() - started:.2f}")
        self.send_header("X-Model", MODEL_NAME)
        self.end_headers()
        self.wfile.write(audio)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))


def main() -> None:
    if not REFERENCE.is_file():
        sys.exit(f"TTS_REFERENCE_WAV is not a file: {REFERENCE!s}")
    load()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"{MODEL_NAME} on 127.0.0.1:{PORT}, voice {REFERENCE.name}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
