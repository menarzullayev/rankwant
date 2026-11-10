"""Playlists and the AES key of a lesson's HLS video (ADR-0056 § 3.5).

The same door as the lesson itself (`services.check_open`): a guest, a
reader who has not enrolled, or one the lesson is still locked for gets
nothing — not the playlist, and above all not the key. Segments are
encrypted, so where they are served from does not matter; the key is the
lock and is never cached (`no-store`).
"""

from __future__ import annotations

from typing import Any

from django.http import Http404, HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from courses import hls, progress, services, videos
from courses.models import Lesson, VideoAsset
from courses.views import _lesson

PLAYLIST = "application/vnd.apple.mpegurl"


def _open_asset(request: Request, slug: str, lesson_id: int) -> tuple[Lesson, VideoAsset]:
    lesson = _lesson(slug, lesson_id)
    state = progress.state(lesson.section.module.course, request.user)
    services.check_open(request.user, lesson, state)
    asset = videos.asset_for(lesson)
    if asset is None or not hls.configured():
        raise Http404
    return lesson, asset


def _private(response: HttpResponse, seconds: int) -> HttpResponse:
    response["Cache-Control"] = f"private, max-age={seconds}" if seconds else "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


class LessonMasterPlaylistView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Dars videosining master pleylisti", responses={(200, PLAYLIST): OpenApiTypes.STR}
    )
    def get(self, request: Request, slug: str, lesson_id: int) -> Any:
        _lesson_row, asset = _open_asset(request, slug, lesson_id)
        return _private(
            HttpResponse(hls.master_playlist(asset.heights), content_type=PLAYLIST), 300
        )


class LessonVariantPlaylistView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Dars videosining bitta sifat pleylisti",
        responses={(200, PLAYLIST): OpenApiTypes.STR},
    )
    def get(self, request: Request, slug: str, lesson_id: int, height: int) -> Any:
        _lesson_row, asset = _open_asset(request, slug, lesson_id)
        if height not in asset.heights:
            raise Http404
        # Relative: the key sits beside this playlist, under the same door.
        text = hls.variant_playlist(asset.key, height, "key")
        # Signed segment addresses expire in an hour; the playlist must not
        # outlive them in a cache.
        return _private(HttpResponse(text, content_type=PLAYLIST), 60)


class LessonVideoKeyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Dars videosining AES-128 kaliti",
        responses={(200, "application/octet-stream"): OpenApiTypes.BINARY},
    )
    def get(self, request: Request, slug: str, lesson_id: int) -> Any:
        _lesson_row, asset = _open_asset(request, slug, lesson_id)
        return _private(
            HttpResponse(bytes(asset.aes_key), content_type="application/octet-stream"), 0
        )
