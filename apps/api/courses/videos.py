"""Course video assets: make one from a file, attach it to a lesson.

Encoding is slow (minutes per hour of video), so the asset is created in
`processing` first; a failure is kept on the row, not lost in a log.
"""

from __future__ import annotations

import logging
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
