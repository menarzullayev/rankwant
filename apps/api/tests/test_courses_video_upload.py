"""Course video upload and the video worker's encode (ADR-0056 part 5c)."""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Any

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from courses import hls, videos
from courses.models import Course, CourseTranslation, Lesson, Module, Section, VideoAsset

pytestmark = pytest.mark.django_db


def _client(user: User) -> APIClient:
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def course(user) -> Course:
    c = Course.objects.create(slug="video-kurs")
    CourseTranslation.objects.create(course=c, locale="uz", title="Kurs")
    c.authors.add(user)
    return c


@pytest.fixture
def bucket(settings: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """A fake bucket: multipart calls recorded, objects kept in memory."""
    settings.COURSE_VIDEO_BUCKET = "video"
    settings.COURSE_VIDEO_S3_ENDPOINT = "http://minio.test"
    state: dict[str, Any] = {"objects": {}, "completed": [], "deleted": []}
    monkeypatch.setattr(hls, "start_multipart", lambda key, ctype: f"up-{key}")
    monkeypatch.setattr(
        hls,
        "part_urls",
        lambda key, upload_id, count, expires=0: [f"https://put/{n}" for n in range(1, count + 1)],
    )
    monkeypatch.setattr(
        hls, "complete_multipart", lambda key, uid, parts: state["completed"].append((key, parts))
    )
    monkeypatch.setattr(hls, "delete_object", lambda key: state["deleted"].append(key))
    monkeypatch.setattr(hls, "delete_prefix", lambda prefix: state["deleted"].append(f"{prefix}/"))
    monkeypatch.setattr(hls, "abort_multipart", lambda key, uid: None)
    monkeypatch.setattr(
        hls, "download", lambda key, target: shutil.copy(state["objects"][key], target)
    )

    def upload_tree(key: str, workdir: Path, heights: list[int]) -> None:
        state["uploaded"] = {
            h: sorted(p.name for p in (workdir / str(h)).iterdir()) for h in heights
        }

    monkeypatch.setattr(hls, "upload_tree", upload_tree)
    return state


def _start(user: User, course: Course, **data: Any) -> Any:
    url = reverse("studio-course-video-list", args=[course.slug])
    return _client(user).post(
        url, {"filename": "dars.mp4", "size": 40 * 1024**2, **data}, format="json"
    )


class TestStart:
    def test_without_a_bucket_upload_is_unavailable(self, user, course, settings):
        settings.COURSE_VIDEO_BUCKET = ""
        resp = _start(user, course)
        assert resp.status_code == 503
        assert resp.json()["error"]["code"] == "course_video_unavailable"

    def test_parts_cover_the_file(self, user, course, bucket):
        resp = _start(user, course, size=40 * 1024**2, heights=[720, 999])
        assert resp.status_code == 201, resp.json()
        body = resp.json()
        assert body["part_size"] == 16 * 1024**2
        assert len(body["parts"]) == 3
        asset = VideoAsset.objects.get()
        assert (asset.status, asset.source, asset.requested_heights) == ("uploading", "file", [720])
        assert asset.source_key.startswith("uploads/") and asset.source_key.endswith("/source.mp4")
        assert "aes" not in str(body)

    def test_a_zip_is_a_ready_hls(self, user, course, bucket):
        assert _start(user, course, filename="tayyor.zip").status_code == 201
        assert VideoAsset.objects.get().source == VideoAsset.Source.HLS_ZIP

    @pytest.mark.parametrize(("filename", "size"), [("dars.exe", 100), ("dars.mp4", 9 * 1024**3)])
    def test_wrong_type_or_size_is_refused(self, user, course, bucket, filename, size):
        resp = _start(user, course, filename=filename, size=size)
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "course_video_refused"

    def test_three_in_flight_at_most(self, user, course, bucket):
        for _ in range(videos.MAX_IN_FLIGHT):
            assert _start(user, course).status_code == 201
        assert _start(user, course).status_code == 400

    def test_another_users_course_is_404(self, other_user, course, bucket):
        assert _start(other_user, course).status_code == 404


class TestComplete:
    def test_complete_queues_the_encode(
        self, user, course, bucket, monkeypatch, django_capture_on_commit_callbacks
    ):
        queued: list[int] = []
        from courses import tasks

        monkeypatch.setattr(tasks.encode_video, "delay", lambda pk: queued.append(pk))
        asset_id = _start(user, course).json()["video"]["id"]
        url = reverse("studio-course-video-complete", args=[course.slug, asset_id])
        with django_capture_on_commit_callbacks(execute=True):
            resp = _client(user).post(url, {"parts": [{"number": 1, "etag": '"a"'}]}, format="json")
        assert resp.status_code == 200
        assert resp.json()["status"] == "queued"
        assert queued == [asset_id]
        assert bucket["completed"][0][1] == [{"number": 1, "etag": '"a"'}]
        again = _client(user).post(url, {"parts": [{"number": 1, "etag": '"a"'}]}, format="json")
        assert again.status_code == 400


class TestDiscard:
    def test_a_video_a_lesson_plays_is_kept(self, user, course, bucket):
        asset = VideoAsset.objects.create(
            course=course,
            key="v/used",
            aes_key=b"k" * 16,
            status=VideoAsset.Status.READY,
            heights=[360],
        )
        module = Module.objects.create(course=course, order=1)
        section = Section.objects.create(module=module, order=1)
        lesson = Lesson.objects.create(section=section, order=1)
        videos.attach(lesson, asset)
        url = reverse("studio-course-video-detail", args=[course.slug, asset.pk])
        assert _client(user).delete(url).status_code == 400
        Lesson.objects.filter(pk=lesson.pk).update(video_ref="")
        assert _client(user).delete(url).status_code == 204
        assert "v/used/" in bucket["deleted"]
        assert not VideoAsset.objects.exists()

    def test_only_ready_videos_attach_in_the_studio(self, user, course, bucket):
        VideoAsset.objects.create(
            course=course, key="v/wip", aes_key=b"k" * 16, status=VideoAsset.Status.PROCESSING
        )
        module = Module.objects.create(course=course, order=1)
        section = Section.objects.create(module=module, order=1)
        lesson = Lesson.objects.create(section=section, order=1)
        url = reverse("studio-course-lesson-detail", args=[course.slug, lesson.pk])
        resp = _client(user).patch(
            url, {"kind": "video", "video_provider": "hls", "video_ref": "v/wip"}, format="json"
        )
        assert resp.status_code == 400


def _sample(path: Path, size: str = "1280x720", seconds: int = 3) -> Path:
    subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={size}:rate=25:duration={seconds}",
            "-f",
            "lavfi",
            "-i",
            f"sine=duration={seconds}",
            "-shortest",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(path),
        ],
        check=True,
    )
    return path


@pytest.mark.skipif(not hls.ffmpeg_available(), reason="ffmpeg is not installed")
class TestWorker:
    def _asset(
        self, course: Course, source: str, source_key: str, heights: list[int]
    ) -> VideoAsset:
        return VideoAsset.objects.create(
            course=course,
            key="v/job",
            aes_key=b"0123456789abcdef",
            status=VideoAsset.Status.QUEUED,
            source=source,
            source_key=source_key,
            requested_heights=heights,
        )

    def test_a_file_is_encoded_up_to_its_own_height(self, course, bucket, tmp_path):
        bucket["objects"]["uploads/job/source.mp4"] = _sample(tmp_path / "in.mp4", "854x480")
        asset = self._asset(course, "file", "uploads/job/source.mp4", [360, 720])
        videos.encode_asset(asset.pk)
        asset.refresh_from_db()
        assert (asset.status, asset.heights, asset.seconds, asset.error) == ("ready", [360], 3, "")
        assert "index.m3u8" in bucket["uploaded"][360]
        assert "uploads/job/source.mp4" in bucket["deleted"]

    def test_a_ready_hls_zip_is_encrypted_without_re_encoding(self, course, bucket, tmp_path):
        source = _sample(tmp_path / "in.mp4", "640x360")
        folder = tmp_path / "hls"
        (folder / "low").mkdir(parents=True)
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(source),
                "-c",
                "copy",
                "-f",
                "hls",
                "-hls_time",
                "2",
                "-hls_playlist_type",
                "vod",
                str(folder / "low" / "index.m3u8"),
            ],
            check=True,
        )
        archive = tmp_path / "ready.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            for path in folder.rglob("*"):
                zf.write(path, path.relative_to(folder).as_posix())
        bucket["objects"]["uploads/job/source.zip"] = archive
        asset = self._asset(course, "hls_zip", "uploads/job/source.zip", [])
        videos.encode_asset(asset.pk)
        asset.refresh_from_db()
        assert (asset.status, asset.heights) == ("ready", [360]), asset.error
        assert any(name.endswith(".ts") for name in bucket["uploaded"][360])

    def test_a_zip_escaping_its_folder_fails_cleanly(self, course, bucket, tmp_path):
        archive = tmp_path / "evil.zip"
        with zipfile.ZipFile(archive, "w") as zf:
            zf.writestr("../../outside.m3u8", "#EXTM3U\n")
        bucket["objects"]["uploads/job/source.zip"] = archive
        asset = self._asset(course, "hls_zip", "uploads/job/source.zip", [])
        videos.encode_asset(asset.pk)
        asset.refresh_from_db()
        assert asset.status == "failed"
        assert "outside" in asset.error
        assert not (tmp_path.parent / "outside.m3u8").exists()
