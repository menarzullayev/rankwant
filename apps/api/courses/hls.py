"""Encrypted HLS for course videos (ADR-0056 § 3.5, owner decisions 2026-11-10).

* Renditions go up to the source's own height and never above it; the
  uploader picks which of them to make (`LADDER`).
* Every segment is AES-128 encrypted. Segments may sit in a public bucket
  (R2 behind Cloudflare: free egress, cached); the key is served only by the
  API, to readers the lesson is open to.
* Storage is any S3 (R2 in production, MinIO locally). Without a configured
  bucket, paid video is simply unavailable.

The bucket layout under an asset's key `v/<id>`:

    v/<id>/master.m3u8          variant list, written here
    v/<id>/<height>/index.m3u8  ffmpeg's playlist, key URI = "key"
    v/<id>/<height>/seg00000.ts encrypted segments
"""

from __future__ import annotations

import functools
import json
import logging
import secrets
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import boto3
from botocore.config import Config
from django.conf import settings

log = logging.getLogger(__name__)

#: Heights an uploader may pick, with a video bitrate ceiling (kbit/s).
LADDER: dict[int, int] = {360: 800, 480: 1400, 720: 2800, 1080: 5000, 1440: 9000, 2160: 16000}
AUDIO_KBPS = 128
SEGMENT_SECONDS = 6
#: The key URI ffmpeg writes; the API swaps it for its own key address.
KEY_PLACEHOLDER = "key"


class VideoUnavailable(RuntimeError):
    """No video bucket is configured (production before R2 keys are set)."""


def configured() -> bool:
    return bool(settings.COURSE_VIDEO_BUCKET and settings.COURSE_VIDEO_S3_ENDPOINT)


@functools.lru_cache(maxsize=1)
def client() -> Any:
    if not configured():
        raise VideoUnavailable("COURSE_VIDEO_BUCKET is not configured")
    return boto3.client(
        "s3",
        endpoint_url=settings.COURSE_VIDEO_S3_ENDPOINT,
        aws_access_key_id=settings.COURSE_VIDEO_S3_KEY,
        aws_secret_access_key=settings.COURSE_VIDEO_S3_SECRET,
        region_name=settings.COURSE_VIDEO_S3_REGION,
        config=Config(
            connect_timeout=3, read_timeout=10, retries={"max_attempts": 3, "mode": "standard"}
        ),
    )


def read_text(key: str) -> str:
    body = client().get_object(Bucket=settings.COURSE_VIDEO_BUCKET, Key=key)["Body"].read()
    return str(body.decode("utf-8"))


def segment_url(key: str) -> str:
    """Where the browser fetches an encrypted segment.

    A public base (R2 custom domain) when there is one; otherwise a
    short-lived signed address — the segment is encrypted either way.
    """
    base = settings.COURSE_VIDEO_PUBLIC_BASE.rstrip("/")
    if base:
        return f"{base}/{key}"
    return str(
        client().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.COURSE_VIDEO_BUCKET, "Key": key},
            ExpiresIn=3600,
        )
    )


def master_playlist(heights: list[int]) -> str:
    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]
    for height in sorted(heights):
        bandwidth = (LADDER.get(height, 2800) + AUDIO_KBPS) * 1000
        width = round(height * 16 / 9 / 2) * 2
        lines.append(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={width}x{height}")
        lines.append(f"{height}.m3u8")
    return "\n".join(lines) + "\n"


def variant_playlist(asset_key: str, height: int, key_url: str) -> str:
    """ffmpeg's playlist with the key URI and segment addresses filled in."""
    out: list[str] = []
    for line in read_text(f"{asset_key}/{height}/index.m3u8").splitlines():
        if line.startswith("#EXT-X-KEY:"):
            out.append(line.replace(f'URI="{KEY_PLACEHOLDER}"', f'URI="{key_url}"'))
        elif line and not line.startswith("#"):
            out.append(segment_url(f"{asset_key}/{height}/{line.strip()}"))
        else:
            out.append(line)
    return "\n".join(out) + "\n"


@dataclass
class Probe:
    height: int
    seconds: int


def probe(source: Path) -> Probe:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=height:format=duration",
            "-of",
            "json",
            str(source),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    data = json.loads(result.stdout)
    height = int(data["streams"][0]["height"])
    seconds = round(float(data.get("format", {}).get("duration") or 0))
    return Probe(height=height, seconds=seconds)


def pick_heights(source_height: int, wanted: list[int] | None) -> list[int]:
    """The ladder rungs at or below the source; the uploader's choice of them.

    A source below 360p still gets one rendition at its own height.
    """
    allowed = [h for h in LADDER if h <= source_height] or [source_height]
    if not wanted:
        return allowed
    chosen = sorted({h for h in wanted if h in allowed})
    if not chosen:
        raise ValueError(f"None of {wanted} fits a {source_height}p source; choose from {allowed}.")
    return chosen


def new_key() -> tuple[str, bytes]:
    return f"v/{secrets.token_hex(8)}", secrets.token_bytes(16)


def encode(source: Path, heights: list[int], aes_key: bytes, workdir: Path) -> None:
    """Write `<workdir>/<height>/index.m3u8` and its encrypted segments."""
    key_file = workdir / "aes.key"
    key_file.write_bytes(aes_key)
    info = workdir / "key.info"
    # Line 1: the URI written into the playlist; line 2: the key file.
    info.write_text(f"{KEY_PLACEHOLDER}\n{key_file}\n", encoding="utf-8")
    for height in heights:
        out = workdir / str(height)
        out.mkdir()
        kbps = LADDER.get(height, 2800)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(source),
                "-vf",
                f"scale=-2:{height}",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-profile:v",
                "main",
                # Main profile needs 4:2:0; a 4:4:4 or 10-bit source would
                # otherwise refuse to encode (measured with ffmpeg 9).
                "-pix_fmt",
                "yuv420p",
                "-maxrate",
                f"{kbps}k",
                "-bufsize",
                f"{kbps * 2}k",
                "-crf",
                "23",
                "-g",
                str(SEGMENT_SECONDS * 30),
                "-c:a",
                "aac",
                "-b:a",
                f"{AUDIO_KBPS}k",
                "-ac",
                "2",
                "-f",
                "hls",
                "-hls_time",
                str(SEGMENT_SECONDS),
                "-hls_playlist_type",
                "vod",
                "-hls_key_info_file",
                str(info),
                "-hls_segment_filename",
                str(out / "seg%05d.ts"),
                str(out / "index.m3u8"),
            ],
            check=True,
            timeout=6 * 3600,
        )
    key_file.unlink()


def upload_tree(asset_key: str, workdir: Path, heights: list[int]) -> None:
    s3 = client()
    bucket = settings.COURSE_VIDEO_BUCKET
    for height in heights:
        for path in sorted((workdir / str(height)).iterdir()):
            content_type = (
                "application/vnd.apple.mpegurl" if path.suffix == ".m3u8" else "video/mp2t"
            )
            s3.upload_file(
                str(path),
                bucket,
                f"{asset_key}/{height}/{path.name}",
                ExtraArgs={"ContentType": content_type},
            )
    s3.put_object(
        Bucket=bucket,
        Key=f"{asset_key}/master.m3u8",
        Body=master_playlist(heights).encode(),
        ContentType="application/vnd.apple.mpegurl",
    )


def encode_and_store(source: Path, asset_key: str, aes_key: bytes, heights: list[int]) -> None:
    workdir = Path(tempfile.mkdtemp(prefix="rw-hls-"))
    try:
        encode(source, heights, aes_key, workdir)
        upload_tree(asset_key, workdir, heights)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def ffmpeg_available() -> bool:
    return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


# --- Uploads (part 5c): the browser sends the original straight to the bucket.

#: Largest original accepted. Cloudflare's 100 MB request cap is why the
#: upload bypasses the site; the bucket takes multi-gigabyte objects.
MAX_UPLOAD_BYTES = 8 * 1024**3
#: S3 multipart: parts of at least 5 MB, at most 10 000 of them.
MIN_PART = 16 * 1024**2
MAX_PARTS = 10_000
#: A ready HLS zip: how many files and how many bytes once unpacked.
MAX_ZIP_FILES = 20_000
MAX_ZIP_BYTES = 12 * 1024**3


def part_size(size: int) -> int:
    return max(MIN_PART, -(-size // MAX_PARTS))


def start_multipart(key: str, content_type: str) -> str:
    response = client().create_multipart_upload(
        Bucket=settings.COURSE_VIDEO_BUCKET, Key=key, ContentType=content_type
    )
    return str(response["UploadId"])


def part_urls(key: str, upload_id: str, count: int, expires: int = 6 * 3600) -> list[str]:
    s3 = client()
    return [
        str(
            s3.generate_presigned_url(
                "upload_part",
                Params={
                    "Bucket": settings.COURSE_VIDEO_BUCKET,
                    "Key": key,
                    "UploadId": upload_id,
                    "PartNumber": number,
                },
                ExpiresIn=expires,
            )
        )
        for number in range(1, count + 1)
    ]


def complete_multipart(key: str, upload_id: str, parts: list[dict[str, Any]]) -> None:
    client().complete_multipart_upload(
        Bucket=settings.COURSE_VIDEO_BUCKET,
        Key=key,
        UploadId=upload_id,
        MultipartUpload={"Parts": [{"PartNumber": p["number"], "ETag": p["etag"]} for p in parts]},
    )


def abort_multipart(key: str, upload_id: str) -> None:
    client().abort_multipart_upload(
        Bucket=settings.COURSE_VIDEO_BUCKET, Key=key, UploadId=upload_id
    )


def download(key: str, target: Path) -> None:
    client().download_file(settings.COURSE_VIDEO_BUCKET, key, str(target))


def delete_prefix(prefix: str) -> None:
    s3 = client()
    bucket = settings.COURSE_VIDEO_BUCKET
    for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=f"{prefix}/"):
        keys = [{"Key": item["Key"]} for item in page.get("Contents", [])]
        if keys:
            s3.delete_objects(Bucket=bucket, Delete={"Objects": keys})


def delete_object(key: str) -> None:
    client().delete_object(Bucket=settings.COURSE_VIDEO_BUCKET, Key=key)


def unpack_zip(archive: Path, target: Path) -> None:
    """Unpack a ready HLS folder, refusing anything that escapes `target`."""
    import zipfile

    with zipfile.ZipFile(archive) as zf:
        members = zf.infolist()
        if len(members) > MAX_ZIP_FILES:
            raise ValueError("The zip holds too many files.")
        if sum(m.file_size for m in members) > MAX_ZIP_BYTES:
            raise ValueError("The zip is too large once unpacked.")
        root = target.resolve()
        for member in members:
            dest = (target / member.filename).resolve()
            if root != dest and root not in dest.parents:
                raise ValueError("The zip contains a path outside its folder.")
        zf.extractall(target)


def variant_playlists(folder: Path) -> list[Path]:
    """Every media playlist (one with segments) under `folder`."""
    found: list[Path] = []
    for path in sorted(folder.rglob("*.m3u8")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "#EXT-X-KEY" in text and "METHOD=NONE" not in text:
            raise ValueError("An encrypted HLS cannot be imported; upload it unencrypted.")
        if "#EXTINF" in text:
            found.append(path)
    if not found:
        raise ValueError("The zip has no HLS playlist with segments.")
    return found


def import_hls(folder: Path, aes_key: bytes, workdir: Path) -> tuple[list[int], int]:
    """Re-mux every variant of a ready HLS into our encrypted layout.

    The video is not re-encoded (`-c copy`), only re-segmented and
    encrypted. Returns the heights and the length in seconds.
    """
    key_file = workdir / "aes.key"
    key_file.write_bytes(aes_key)
    info = workdir / "key.info"
    info.write_text(f"{KEY_PLACEHOLDER}\n{key_file}\n", encoding="utf-8")
    heights: list[int] = []
    seconds = 0
    try:
        for playlist in variant_playlists(folder):
            found = probe(playlist)
            if found.height in heights:
                continue
            out = workdir / str(found.height)
            out.mkdir()
            subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-allowed_extensions",
                    "ALL",
                    "-protocol_whitelist",
                    "file,crypto,data",
                    "-i",
                    str(playlist),
                    "-c",
                    "copy",
                    "-f",
                    "hls",
                    "-hls_time",
                    str(SEGMENT_SECONDS),
                    "-hls_playlist_type",
                    "vod",
                    "-hls_key_info_file",
                    str(info),
                    "-hls_segment_filename",
                    str(out / "seg%05d.ts"),
                    str(out / "index.m3u8"),
                ],
                check=True,
                timeout=6 * 3600,
            )
            heights.append(found.height)
            seconds = max(seconds, found.seconds)
    finally:
        key_file.unlink(missing_ok=True)
    return sorted(heights), seconds
