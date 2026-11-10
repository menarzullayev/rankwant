"""Course video assets: make one from a file, attach it to a lesson.

Encoding is slow (minutes per hour of video), so the asset is created in
`processing` first; a failure is kept on the row, not lost in a log.
"""

from __future__ import annotations

import logging
import shutil
import tempfile
from pathlib import Path
from typing import Any

from django.db import transaction

from courses import hls
from courses.models import Course, Lesson, VideoAsset

log = logging.getLogger(__name__)


def create_from_file(
    course: Course,
    source: Path,
    *,
    heights: list[int] | None = None,
    user: Any = None,
) -> VideoAsset:
    """Encode `source` into encrypted HLS for `course` and store it."""
    found = hls.probe(source)
    chosen = hls.pick_heights(found.height, heights)
    key, aes_key = hls.new_key()
    asset = VideoAsset.objects.create(
        course=course,
        key=key,
        aes_key=aes_key,
        heights=chosen,
        seconds=found.seconds,
        created_by=user if getattr(user, "is_authenticated", False) else None,
    )
    try:
        hls.encode_and_store(source, key, aes_key, chosen)
    except Exception as error:
        log.exception("course video %s failed", key)
        asset.status = VideoAsset.Status.FAILED
        asset.error = str(error)[:2000]
        asset.save(update_fields=["status", "error"])
        raise
    asset.status = VideoAsset.Status.READY
    asset.save(update_fields=["status"])
    return asset


@transaction.atomic
def attach(lesson: Lesson, asset: VideoAsset) -> Lesson:
    """Make `asset` the lesson's video. Same course only — see `VideoAsset`."""
    if asset.course_id != lesson.section.module.course_id:
        raise ValueError("The video belongs to another course.")
    lesson.kind = Lesson.Kind.VIDEO
    lesson.video_provider = Lesson.VideoProvider.HLS
    lesson.video_ref = asset.key
    lesson.video_seconds = asset.seconds
    lesson.save(update_fields=["kind", "video_provider", "video_ref", "video_seconds"])
    return lesson


def asset_for(lesson: Lesson) -> VideoAsset | None:
    """The lesson's ready HLS asset, if it has one of its own course."""
    if lesson.video_provider != Lesson.VideoProvider.HLS or not lesson.video_ref:
        return None
    return VideoAsset.objects.filter(
        key=lesson.video_ref,
        course_id=lesson.section.module.course_id,
        status=VideoAsset.Status.READY,
    ).first()


# --- Uploads (ADR-0056 part 5c): browser → bucket, then the video worker.

#: Originals in flight per course: uploading, queued or being encoded.
MAX_IN_FLIGHT = 3

_FILE_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
    ".webm": "video/webm",
}
_ZIP_TYPES = {".zip": "application/zip"}

IN_FLIGHT = (
    VideoAsset.Status.UPLOADING,
    VideoAsset.Status.QUEUED,
    VideoAsset.Status.PROCESSING,
)


class UploadRefused(ValueError):
    """The upload cannot start; the message says why (English, API-facing)."""


def start_upload(
    course: Course,
    user: Any,
    *,
    filename: str,
    size: int,
    heights: list[int] | None = None,
) -> tuple[VideoAsset, list[str], int]:
    """Open a multipart upload; the browser PUTs the parts to the URLs."""
    suffix = Path(filename).suffix.lower()
    if suffix in _FILE_TYPES:
        source, content_type = VideoAsset.Source.FILE, _FILE_TYPES[suffix]
    elif suffix in _ZIP_TYPES:
        source, content_type = VideoAsset.Source.HLS_ZIP, _ZIP_TYPES[suffix]
    else:
        raise UploadRefused("Upload an .mp4, .mov, .mkv or .webm video, or a .zip of a ready HLS.")
    if not 0 < size <= hls.MAX_UPLOAD_BYTES:
        raise UploadRefused("The file is empty or larger than 8 GB.")
    wanted = sorted({h for h in heights or [] if h in hls.LADDER})
    if course.videos.filter(status__in=IN_FLIGHT).count() >= MAX_IN_FLIGHT:
        raise UploadRefused("Three videos of this course are already uploading or encoding.")
    key, aes_key = hls.new_key()
    source_key = f"uploads/{key.removeprefix('v/')}/source{suffix}"
    upload_id = hls.start_multipart(source_key, content_type)
    asset = VideoAsset.objects.create(
        course=course,
        key=key,
        aes_key=aes_key,
        status=VideoAsset.Status.UPLOADING,
        source=source,
        requested_heights=wanted,
        source_key=source_key,
        upload_id=upload_id,
        size=size,
        created_by=user if getattr(user, "is_authenticated", False) else None,
    )
    part = hls.part_size(size)
    count = -(-size // part)
    return asset, hls.part_urls(source_key, upload_id, count), part


def complete_upload(asset: VideoAsset, parts: list[dict[str, Any]]) -> VideoAsset:
    """Close the multipart upload and queue the encoding."""
    if asset.status != VideoAsset.Status.UPLOADING:
        raise UploadRefused("This upload is already finished.")
    hls.complete_multipart(asset.source_key, asset.upload_id, parts)
    asset.status = VideoAsset.Status.QUEUED
    asset.save(update_fields=["status"])
    from courses.tasks import encode_video

    transaction.on_commit(lambda: encode_video.delay(asset.pk))
    return asset


def discard(asset: VideoAsset) -> None:
    """Remove an asset no lesson uses, with everything it stored."""
    if Lesson.objects.filter(video_provider=Lesson.VideoProvider.HLS, video_ref=asset.key).exists():
        raise UploadRefused("A lesson plays this video; detach it first.")
    if asset.status == VideoAsset.Status.UPLOADING and asset.upload_id:
        try:
            hls.abort_multipart(asset.source_key, asset.upload_id)
        except Exception:
            log.warning("abort of %s failed", asset.key, exc_info=True)
    if asset.source_key:
        hls.delete_object(asset.source_key)
    hls.delete_prefix(asset.key)
    asset.delete()


def encode_asset(asset_id: int) -> None:
    """The video worker's job: original in the bucket → encrypted HLS."""
    asset = VideoAsset.objects.select_related("course").get(pk=asset_id)
    if asset.status not in (VideoAsset.Status.QUEUED, VideoAsset.Status.PROCESSING):
        return
    asset.status = VideoAsset.Status.PROCESSING
    asset.save(update_fields=["status"])
    workdir = Path(tempfile.mkdtemp(prefix="rw-video-"))
    try:
        original = workdir / Path(asset.source_key).name
        hls.download(asset.source_key, original)
        out = workdir / "out"
        out.mkdir()
        if asset.source == VideoAsset.Source.HLS_ZIP:
            unpacked = workdir / "unpacked"
            unpacked.mkdir()
            hls.unpack_zip(original, unpacked)
            heights, seconds = hls.import_hls(unpacked, bytes(asset.aes_key), out)
        else:
            found = hls.probe(original)
            heights = hls.pick_heights(found.height, asset.requested_heights or None)
            seconds = found.seconds
            hls.encode(original, heights, bytes(asset.aes_key), out)
        hls.upload_tree(asset.key, out, heights)
    except Exception as error:
        log.exception("course video %s failed", asset.key)
        asset.status = VideoAsset.Status.FAILED
        asset.error = str(error)[:2000]
        asset.save(update_fields=["status", "error"])
        return
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    hls.delete_object(asset.source_key)
    asset.status = VideoAsset.Status.READY
    asset.heights = heights
    asset.seconds = seconds
    asset.error = ""
    asset.save(update_fields=["status", "heights", "seconds", "error"])
