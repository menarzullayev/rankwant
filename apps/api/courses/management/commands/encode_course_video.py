"""Encode a video file into a course's encrypted HLS and attach it to a lesson.

    python manage.py encode_course_video <course-slug> <file> [--heights 360,720] [--lesson <id>]

Staff tool until the studio upload (ADR-0056 part 5c). Needs ffmpeg and a
configured video bucket (`COURSE_VIDEO_BUCKET`).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from courses import hls, videos
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = "Encode a video into a course's encrypted HLS and optionally attach it to a lesson."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("course")
        parser.add_argument("file")
        parser.add_argument(
            "--heights", default="", help="e.g. 360,720,1080 (default: every rung up to the source)"
        )
        parser.add_argument(
            "--lesson", type=int, help="lesson id of the same course to attach the video to"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not hls.configured():
            raise CommandError("COURSE_VIDEO_BUCKET / COURSE_VIDEO_S3_ENDPOINT are not set.")
        if not hls.ffmpeg_available():
            raise CommandError("ffmpeg and ffprobe must be on PATH.")
        source = Path(options["file"])
        if not source.is_file():
            raise CommandError(f"No such file: {source}")
        course = Course.objects.filter(slug=options["course"]).first()
        if course is None:
            raise CommandError(f"No course {options['course']!r}.")
        lesson = None
        if options["lesson"]:
            lesson = Lesson.objects.filter(
                pk=options["lesson"], section__module__course=course
            ).first()
            if lesson is None:
                raise CommandError("That lesson is not in this course.")
        heights = [int(h) for h in options["heights"].split(",") if h.strip()] or None
        try:
            asset = videos.create_from_file(course, source, heights=heights)
        except ValueError as error:
            raise CommandError(str(error)) from error
        self.stdout.write(f"{asset.key}: {asset.heights}, {asset.seconds} s")
        if lesson is not None:
            videos.attach(lesson, asset)
            self.stdout.write(f"attached to lesson {lesson.pk}")
