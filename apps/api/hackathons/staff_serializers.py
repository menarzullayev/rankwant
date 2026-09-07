"""Staff (admin UI) serializerlari — hakaton va uning loyihalari.

Ommaviy `serializers.py` o'zgarmaydi: bu yerda `is_public`, `scored_by`
kabi faqat xodimga kerak maydonlar ochiladi.
"""

from __future__ import annotations

from rest_framework import serializers

from hackathons.models import Hackathon, HackathonSubmission


class StaffHackathonSerializer(serializers.ModelSerializer[Hackathon]):
    submission_count = serializers.SerializerMethodField()
    accepts_submissions = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(read_only=True)

    def get_submission_count(self, obj: Hackathon) -> int:
        # Ro'yxatda queryset annotatsiyasi; yaratish/tahrirlash javobida u yo'q.
        count: int | None = getattr(obj, "submission_count", None)
        return count if count is not None else obj.submissions.count()

    class Meta:
        model = Hackathon
        fields = [
            "slug",
            "title",
            "description",
            "start_at",
            "submission_deadline",
            "end_at",
            "is_public",
            "created_at",
            "submission_count",
            "accepts_submissions",
            "is_finished",
        ]
        read_only_fields = ["created_at"]


class StaffSubmissionSerializer(serializers.ModelSerializer[HackathonSubmission]):
    username = serializers.CharField(source="user.username", read_only=True)
    scored_by = serializers.CharField(source="scored_by.username", read_only=True, default=None)

    class Meta:
        model = HackathonSubmission
        fields = [
            "id",
            "username",
            "team_name",
            "title",
            "description",
            "repo_url",
            "demo_url",
            "submitted_at",
            "score",
            "feedback",
            "scored_by",
            "scored_at",
        ]
        read_only_fields = fields
