"""Encrypted HLS of course videos (ADR-0056 § 3.5, part 5b)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from courses import hls, videos
from courses.models import (
    Course,
    CourseTranslation,
    Enrollment,
    Lesson,
    LessonTranslation,
    Module,
    Section,
    VideoAsset,
)

pytestmark = pytest.mark.django_db

VARIANT = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXT-X-PLAYLIST-TYPE:VOD
#EXT-X-KEY:METHOD=AES-128,URI="key"
#EXTINF:6.0,
seg00000.ts
#EXTINF:2.5,
seg00001.ts
#EXT-X-ENDLIST
"""


def _client(user: User | None = None) -> APIClient:
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


@pytest.fixture
def video_bucket(settings: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    settings.COURSE_VIDEO_BUCKET = "video"
    settings.COURSE_VIDEO_S3_ENDPOINT = "http://minio.test"
    settings.COURSE_VIDEO_PUBLIC_BASE = "https://video.example"
    stored = {"v/abc/720/index.m3u8": VARIANT}
    monkeypatch.setattr(hls, "read_text", lambda key: stored[key])
    return stored


def _course_with_video(
    slug: str = "pullik", access: str = Course.Access.FREE
) -> tuple[Course, Lesson, VideoAsset]:
    course = Course.objects.create(slug=slug, is_published=True, access=access, price_uzs=1000)
    CourseTranslation.objects.create(course=course, locale="uz", title="Kurs", summary="s")
    module = Module.objects.create(course=course, order=1)
    section = Section.objects.create(module=module, order=1)
    lesson = Lesson.objects.create(section=section, order=1, kind=Lesson.Kind.TEXT)
    LessonTranslation.objects.create(lesson=lesson, locale="uz", title="Video dars")
    asset = VideoAsset.objects.create(
        course=course,
        key="v/abc" if slug == "pullik" else f"v/{slug}",
        aes_key=b"0123456789abcdef",
        heights=[360, 720],
        seconds=8,
        status=VideoAsset.Status.READY,
    )
    videos.attach(lesson, asset)
    return course, lesson, asset


def _url(name: str, course: Course, lesson: Lesson, **extra: Any) -> str:
    return reverse(name, kwargs={"slug": course.slug, "lesson_id": lesson.pk, **extra})


class TestKeyDoor:
    def test_guest_gets_no_key(self, video_bucket):
        course, lesson, _ = _course_with_video()
        assert _client().get(_url("course-lesson-hls-key", course, lesson)).status_code == 401

    def test_reader_who_has_not_enrolled_gets_no_key(self, video_bucket, user):
        course, lesson, _ = _course_with_video()
        assert _client(user).get(_url("course-lesson-hls-key", course, lesson)).status_code == 403

    def test_enrolled_reader_gets_the_key_never_cached(self, video_bucket, user):
        course, lesson, asset = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        resp = _client(user).get(_url("course-lesson-hls-key", course, lesson))
        assert resp.status_code == 200
        assert resp.content == bytes(asset.aes_key)
        assert resp["Cache-Control"] == "private, no-store"

    def test_no_bucket_means_no_video(self, settings, user):
        settings.COURSE_VIDEO_BUCKET = ""
        course, lesson, _ = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        assert _client(user).get(_url("course-lesson-hls-key", course, lesson)).status_code == 404


class TestPlaylists:
    def test_master_lists_the_renditions(self, video_bucket, user):
        course, lesson, _ = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        resp = _client(user).get(_url("course-lesson-hls-master", course, lesson))
        assert resp.status_code == 200
        assert resp["Content-Type"] == "application/vnd.apple.mpegurl"
        text = resp.content.decode()
        assert "RESOLUTION=640x360\n360.m3u8" in text
        assert "RESOLUTION=1280x720\n720.m3u8" in text

    def test_variant_points_segments_at_the_bucket_and_the_key_at_the_api(self, video_bucket, user):
        course, lesson, _ = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        resp = _client(user).get(_url("course-lesson-hls-variant", course, lesson, height=720))
        text = resp.content.decode()
        assert 'URI="key"' in text
        assert "https://video.example/v/abc/720/seg00000.ts" in text
        assert "\nseg00001.ts" not in text

    def test_unknown_height_is_404(self, video_bucket, user):
        course, lesson, _ = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        url = _url("course-lesson-hls-variant", course, lesson, height=1080)
        assert _client(user).get(url).status_code == 404

    def test_lesson_detail_names_the_playlist_not_the_key(self, video_bucket, user):
        course, lesson, _ = _course_with_video()
        Enrollment.objects.create(user=user, course=course)
        body = _client(user).get(reverse("course-lesson", args=[course.slug, lesson.pk])).json()
        assert (
            body["video"]["playlist"]
            == f"/courses/{course.slug}/lessons/{lesson.pk}/hls/master.m3u8"
        )
        assert body["video"]["ref"] is None
        assert "v/abc" not in str(body)


class TestOwnCourseOnly:
    def test_attach_refuses_another_courses_video(self):
        _course, lesson, _ = _course_with_video()
        _other, _l, foreign = _course_with_video("boshqa")
        with pytest.raises(ValueError):
            videos.attach(lesson, foreign)

    def test_studio_attaches_only_this_courses_video(self, user):
        course, lesson, _asset = _course_with_video()
        _other, _l, foreign = _course_with_video("boshqa")
        course.authors.add(user)
        Course.objects.filter(pk=course.pk).update(is_published=False)
        url = reverse("studio-course-lesson-detail", args=[course.slug, lesson.pk])
        refused = _client(user).patch(
            url, {"video_provider": "hls", "video_ref": foreign.key}, format="json"
        )
        assert refused.status_code == 400
        own = _client(user).patch(
            url, {"video_provider": "hls", "video_ref": "v/abc"}, format="json"
        )
        assert own.status_code == 200, own.json()

    def test_a_foreign_ref_never_opens_a_key(self, video_bucket, user):
        """Even a row written past the studio (admin, a bug) gives nothing."""
        course, lesson, _ = _course_with_video()
        _other, _l, foreign = _course_with_video("boshqa")
        Lesson.objects.filter(pk=lesson.pk).update(video_ref=foreign.key)
        Enrollment.objects.create(user=user, course=course)
        assert _client(user).get(_url("course-lesson-hls-key", course, lesson)).status_code == 404


class TestLadder:
    def test_never_above_the_source(self):
        assert hls.pick_heights(720, None) == [360, 480, 720]
        assert hls.pick_heights(2160, [1080, 360]) == [360, 1080]
        assert hls.pick_heights(240, None) == [240]

    def test_a_choice_above_the_source_is_refused(self):
        with pytest.raises(ValueError):
            hls.pick_heights(720, [1080])


@pytest.mark.skipif(not hls.ffmpeg_available(), reason="ffmpeg is not installed")
class TestEncode:
    def test_real_encode_is_encrypted_and_playable_with_the_key(self, tmp_path: Path):
        source = tmp_path / "in.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc=size=1280x720:rate=30:duration=3",
                "-f",
                "lavfi",
                "-i",
                "sine=frequency=440:duration=3",
                "-shortest",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                str(source),
            ],
            check=True,
        )
        found = hls.probe(source)
        assert (found.height, found.seconds) == (720, 3)
        out = tmp_path / "out"
        out.mkdir()
        hls.encode(source, [360], b"0123456789abcdef", out)
        playlist = (out / "360" / "index.m3u8").read_text()
        assert 'METHOD=AES-128,URI="key"' in playlist
        assert not (out / "aes.key").exists()
        segment = next((out / "360").glob("seg*.ts"))
        # Encrypted: an MPEG-TS packet starts with 0x47; the ciphertext does not.
        assert segment.read_bytes()[0] != 0x47
        # …and it decodes with the key: rewrite the URI to the key file.
        (out / "k.bin").write_bytes(b"0123456789abcdef")
        local = out / "360" / "local.m3u8"
        local.write_text(playlist.replace('URI="key"', f'URI="{(out / "k.bin").as_posix()}"'))
        decoded = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-allowed_extensions",
                "ALL",
                "-protocol_whitelist",
                "file,crypto,data",
                "-show_entries",
                "stream=height",
                "-of",
                "csv=p=0",
                str(local),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        assert "360" in decoded.stdout
        shutil.rmtree(out)
