"""Course video encoding runs on its own queue (`video`), served only by the
`video-worker` service, so a long encode never delays judge results
(owner decision 2026-11-10)."""

from __future__ import annotations

from celery import shared_task

from courses import videos


@shared_task(name="courses.encode_video", acks_late=True)
def encode_video(asset_id: int) -> None:
    videos.encode_asset(asset_id)
